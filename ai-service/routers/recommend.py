from typing import List, Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class RecommendRequest(BaseModel):
    user_skills: List[str] = []
    preferred_domains: List[str] = []
    difficulty: str = "intermediate"
    duration: str = "3months"
    language: str = "fr"

class ProjectSuggestion(BaseModel):
    title: str
    description: str
    domain: str
    technologies: str
    difficulty: str
    duration: str
    score: float
    reason: str


class RecommendResponse(BaseModel):
    suggestions: List[ProjectSuggestion]
    total: int


import httpx
import os

# Project database will be fetched from backend
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")

@router.post("/recommend", response_model=RecommendResponse)
async def recommend_projects(request: RecommendRequest):
    """Generate project recommendations based on user skills and preferences."""
    try:
        # Fetch projects from backend with language awareness
        headers = {"Accept-Language": request.language}
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/projects/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                projects = data.get("results", []) if isinstance(data, dict) else data
            else:
                projects = []
    except Exception as e:
        print(f"Error fetching projects: {e}")
        projects = []

    suggestions = []
    user_skills_lower = [s.lower() for s in request.user_skills]

    for project in projects:
        score = 0.0
        matched = []

        # Skill matching (40% weight)
        techs = [t.strip().lower() for t in project.get("technologies", "").split(",")]
        skill_matches = sum(1 for s in user_skills_lower if any(s in t for t in techs))
        if techs:
            skill_score = skill_matches / len(techs)
            score += skill_score * 0.4
            matched = [s for s in request.user_skills if any(s.lower() in t for t in techs)]

        # Domain matching (30% weight)
        if project.get("domain") in request.preferred_domains:
            score += 0.3

        # Difficulty matching (20% weight)
        if project.get("difficulty") == request.difficulty:
            score += 0.2
        elif (
            (request.difficulty == "intermediate" and project.get("difficulty") == "beginner")
            or (request.difficulty == "advanced" and project.get("difficulty") == "intermediate")
        ):
            score += 0.1

        # Base score (10%)
        score += 0.1

        if score >= 0.2:
            # Localize the reason
            if request.language.startswith('en'):
                reason = f"Matches {len(matched)} of your skills"
                if project.get("domain") in request.preferred_domains:
                    reason += f" and the domain {project.get('domain')}"
            else:
                reason = f"Correspond à {len(matched)} de vos compétences"
                if project.get("domain") in request.preferred_domains:
                    reason += f" et au domaine {project.get('domain')}"

            suggestions.append(ProjectSuggestion(
                title=project.get("title", "Sans titre" if request.language == "fr" else "Untitled"),
                description=project.get("description", ""),
                domain=project.get("domain", "Autre" if request.language == "fr" else "Other"),
                technologies=project.get("technologies", ""),
                difficulty=project.get("difficulty", "intermediate"),
                duration=request.duration,
                score=round(score, 2),
                reason=reason,
            ))

    # Sort by score
    suggestions.sort(key=lambda x: x.score, reverse=True)

    return RecommendResponse(
        suggestions=suggestions[:5],
        total=len(suggestions),
    )
