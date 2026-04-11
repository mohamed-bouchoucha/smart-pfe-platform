import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

router = APIRouter()

class SkillGapRequest(BaseModel):
    student_name: str
    student_skills_with_levels: str
    project_title: str
    project_domain: str
    project_description: str
    required_skills: str
    optional_skills: str = ""
    supervisor_name: str
    language: str = "fr"

class SkillGapResponse(BaseModel):
    report: str
    metadata: dict = {}

class LearningPathRequest(BaseModel):
    student_name: str
    gap_skills_list: str
    related_skills: str = "Aucune pertinente trouvée"
    hours_per_week: int = 10
    learning_style: str = ""
    pfe_deadline: str = "Dans 3 mois"
    language: str = "fr"

class LearningPathResponse(BaseModel):
    roadmap: str
    metadata: dict = {}

SKILL_GAP_PROMPT = """
You are ARIA, a skill assessment specialist at the Smart PFE Platform.

## Student Skills
Declared skills and estimated proficiency levels:
{student_skills_with_levels}
Example format: [{{"skill": "Python", "level": "advanced"}}, {{"skill": "React", "level": "intermediate"}}]

## Target Project
- Title: {project_title}
- Domain: {project_domain}
- Required skills: {required_skills}
- Nice-to-have skills: {optional_skills}
- Supervisor: {supervisor_name}
- Project description: {project_description}

## Task
Perform a detailed skill gap analysis. Your output must include:

### 1. Overall Readiness Score (0–100)
Explain the score in 1 sentence.

### 2. Matched Skills
List skills the student already has that are directly relevant. For each, note their proficiency and whether it is sufficient for the project.

### 3. Critical Gaps
Skills that are required for the project but missing or insufficient. For each gap:
- Skill name
- Why it matters for this project (project-specific reason, not generic)
- Estimated time to reach working proficiency (e.g., "3–4 weeks of focused study")

### 4. Optional Gaps
Nice-to-have skills the student doesn't have. Briefly note them but don't alarm the student.

### 5. Personalized Learning Path
For each critical gap, provide:
- 1 free online resource (Coursera, fast.ai, official docs, YouTube channel — be specific with URL if known)
- 1 practical mini-project to build that skill in the context of this PFE project

### 6. Recommendation
A direct, honest 2-sentence verdict: should this student apply? What should they do in the next 2 weeks?

## Tone
Be honest about gaps but encouraging. Frame gaps as growth opportunities, not disqualifiers. Use the student's name ({student_name}) at least once.

Return your analysis in well-structured markdown.
"""

LEARNING_PATH_PROMPT = """
You are ARIA, creating a personalized learning plan for {student_name}.

## Skills to Learn
{gap_skills_list}
Each item includes the skill name and the PFE project it is needed for.

## Student Context
- Current level in related areas: {related_skills}
- Available time per week: {hours_per_week} hours
- Learning style preference (if known): {learning_style}
- PFE start deadline: {pfe_deadline}

## Task
Create a week-by-week learning roadmap that fits within the time available before the PFE deadline.

For each week, specify:
- **Focus skill**
- **Learning objective** (what they will be able to do by end of week)
- **Primary resource** (name, URL, estimated hours)
- **Mini-project** (small practical task, 2–4 hours, directly related to the PFE domain)
- **Check-in question** (one question the student should be able to answer at the end of the week to self-assess)

## Rules
- Prioritize free resources (official docs, fast.ai, CS50, YouTube channels, GitHub repos)
- Sequence skills logically — don't assign advanced topics before prerequisites
- Keep each week to exactly {hours_per_week} hours of content
- End the roadmap with a "capstone mini-project" that combines all learned skills

Return the roadmap in structured markdown with clear week headers.
"""

def get_llm(temperature: float):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-gemini-api-key-here":
        return None
    return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=temperature, google_api_key=api_key)

@router.post("/analyze-fit", response_model=SkillGapResponse)
async def analyze_fit(request: SkillGapRequest):
    """Perform a detailed skill gap analysis."""
    llm = get_llm(temperature=0.3)
    if not llm:
        return SkillGapResponse(
            report="Le service d'analyse IA est actuellement hors-ligne. Veuillez réessayer plus tard.",
            metadata={"provider": "fallback"}
        )

    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", SKILL_GAP_PROMPT)
        ])
        chain = prompt | llm
        
        response = chain.invoke({
            "student_name": request.student_name,
            "student_skills_with_levels": request.student_skills_with_levels,
            "project_title": request.project_title,
            "project_domain": request.project_domain,
            "project_description": request.project_description,
            "required_skills": request.required_skills,
            "optional_skills": request.optional_skills,
            "supervisor_name": request.supervisor_name
        })
        
        return SkillGapResponse(
            report=response.content,
            metadata={"provider": "gemini", "model": "gemini-1.5-pro"}
        )
    except Exception as e:
        print(f"Langchain Skill Gap error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'analyse des compétences.")

@router.post("/learning-path", response_model=LearningPathResponse)
async def generate_learning_path(request: LearningPathRequest):
    """Generate a personalized learning path."""
    llm = get_llm(temperature=0.4)
    if not llm:
        return LearningPathResponse(
            roadmap="Le service IA est actuellement hors-ligne. Veuillez consulter des plateformes comme Coursera ou YouTube.",
            metadata={"provider": "fallback"}
        )

    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", LEARNING_PATH_PROMPT)
        ])
        chain = prompt | llm
        
        response = chain.invoke({
            "student_name": request.student_name,
            "gap_skills_list": request.gap_skills_list,
            "related_skills": request.related_skills,
            "hours_per_week": request.hours_per_week,
            "learning_style": request.learning_style,
            "pfe_deadline": request.pfe_deadline
        })
        
        return LearningPathResponse(
            roadmap=response.content,
            metadata={"provider": "gemini", "model": "gemini-1.5-pro"}
        )
    except Exception as e:
        print(f"Langchain Learning Path error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la génération du plan d'apprentissage.")
