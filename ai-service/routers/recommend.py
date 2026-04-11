import json
import os
import httpx
from typing import List, Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

router = APIRouter()

class RecommendRequest(BaseModel):
    user_skills: List[str] = []
    preferred_domains: List[str] = []
    difficulty: str = "intermediate"
    duration: str = "3months"
    language: str = "fr"
    user_profile: dict = {}

class ProjectSuggestion(BaseModel):
    project_id: int
    title: str
    match_score: float
    why_it_fits: str
    skill_gaps: List[str] = []
    gap_effort: str = "Low"

class RecommendResponse(BaseModel):
    suggestions: List[ProjectSuggestion]
    total: int

RECOMMENDATION_PROMPT = """
You are ARIA, the AI matching engine of the Smart PFE Platform.

## Student Profile
- Name: {student_name}
- Academic level: {academic_level}
- Skills: {skills_list}
- Completed courses: {courses_list}
- Preferred domains (if stated): {preferred_domains}
- Availability: {availability}

## Available Projects
{projects_json}

## Task
Analyze the student's profile against all available projects and return a ranked list of the TOP 5 most suitable projects.

For each recommended project, provide:
1. **project_id** (must match exactly the ID in the catalog)
2. **title** (exact, from the catalog)
3. **match_score** (0–100, based on skill overlap, domain alignment, and academic level fit)
4. **why_it_fits** (2–3 sentences, specific to THIS student's profile — mention their actual skills)
5. **skill_gaps** (if any — list missing skills honestly, max 3)
6. **gap_effort** (Low / Medium / High)

## Output Format
Return a valid JSON array. No markdown, no prose outside the JSON.

[
  {{
    "project_id": 1,
    "title": "...",
    "match_score": 94,
    "why_it_fits": "...",
    "skill_gaps": ["..."],
    "gap_effort": "Low"
  }}
]
"""

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

def get_llm(temperature: float = 0.2):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-gemini-api-key-here":
        return None
    return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=temperature, google_api_key=api_key)

@router.post("/recommend", response_model=RecommendResponse)
async def recommend_projects(request: RecommendRequest):
    """Generate project recommendations based on user skills and preferences using LangChain."""
    try:
        headers = {"Accept-Language": request.language}
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BACKEND_URL}/projects/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                projects = data.get("results", []) if isinstance(data, dict) else data
            else:
                projects = []
    except Exception as e:
        print(f"Error fetching projects: {e}")
        projects = []
        
    if not projects:
        return RecommendResponse(suggestions=[], total=0)
        
    llm = get_llm(temperature=0.2)
    if not llm:
        # Fallback to local static filtering if no API key
        suggestions = []
        user_skills_lower = [s.lower() for s in request.user_skills]
        for p in projects:
            techs = [t.strip().lower() for t in p.get("technologies", "").split(",")]
            score = sum(1 for s in user_skills_lower if any(s in t for t in techs)) / max(len(techs), 1) * 100
            suggestions.append(ProjectSuggestion(
                project_id=p.get("id", 0),
                title=p.get("title", "Sans titre"),
                match_score=round(score, 1),
                why_it_fits="Correspond au profil par défaut (mode fallback).",
                skill_gaps=[],
                gap_effort="Low"
            ))
        suggestions.sort(key=lambda x: x.match_score, reverse=True)
        return RecommendResponse(suggestions=suggestions[:5], total=len(suggestions))

    p = request.user_profile
    student_name = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip() or "Étudiant"
    academic_level = p.get('academic_level', 'Non spécifié')
    skills_list = ", ".join(request.user_skills) if request.user_skills else "Aucune"
    preferred_domains = ", ".join(request.preferred_domains) if request.preferred_domains else "Aucun"
    availability = request.duration

    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", RECOMMENDATION_PROMPT)
        ])
        
        parser = JsonOutputParser()
        chain = prompt | llm | parser
        
        projects_json = json.dumps(projects, ensure_ascii=False)
        
        result = chain.invoke({
            "student_name": student_name,
            "academic_level": academic_level,
            "skills_list": skills_list,
            "courses_list": p.get("courses_list", "Non spécifiés"),
            "preferred_domains": preferred_domains,
            "availability": availability,
            "projects_json": projects_json
        })
        
        # Result should be a list of dicts
        suggestions = []
        for r in result:
            suggestions.append(ProjectSuggestion(
                project_id=r.get("project_id", 0),
                title=r.get("title", ""),
                match_score=float(r.get("match_score", 0.0)),
                why_it_fits=r.get("why_it_fits", ""),
                skill_gaps=r.get("skill_gaps", []),
                gap_effort=r.get("gap_effort", "Low")
            ))
            
        return RecommendResponse(suggestions=suggestions[:5], total=len(suggestions))
        
    except Exception as e:
        print(f"Langchain Recommendation error: {e}")
        # Fallback to local filtering
        return RecommendResponse(suggestions=[], total=0)
