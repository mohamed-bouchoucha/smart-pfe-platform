"""
Recommendation Router — Generates project recommendations based on user skills.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class RecommendRequest(BaseModel):
    user_skills: list[str] = []
    preferred_domains: list[str] = []
    difficulty: str = "intermediate"
    duration: str = "3months"


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
    suggestions: list[ProjectSuggestion]
    total: int


# Project database for recommendations
PROJECT_DATABASE = [
    {
        "title": "Système de recommandation de films avec IA",
        "description": "Moteur de recommandation utilisant le filtrage collaboratif et le NLP pour suggérer des films personnalisés",
        "domain": "IA",
        "technologies": "Python, TensorFlow, Flask, React, PostgreSQL",
        "difficulty": "intermediate",
        "skills": ["python", "tensorflow", "flask", "react", "sql"],
    },
    {
        "title": "Plateforme e-commerce avec chatbot intégré",
        "description": "Application e-commerce full-stack avec assistant d'achat intelligent",
        "domain": "Web",
        "technologies": "React, Django, PostgreSQL, Stripe, Docker",
        "difficulty": "intermediate",
        "skills": ["react", "django", "postgresql", "docker"],
    },
    {
        "title": "Application de monitoring IoT en temps réel",
        "description": "Dashboard de surveillance de capteurs IoT avec alertes et visualisations temps réel",
        "domain": "IoT",
        "technologies": "React, Node.js, MQTT, InfluxDB, Grafana",
        "difficulty": "advanced",
        "skills": ["react", "node.js", "docker"],
    },
    {
        "title": "Scanner de vulnérabilités web automatisé",
        "description": "Outil de pen-testing automatisé détectant les failles OWASP Top 10",
        "domain": "Cybersecurity",
        "technologies": "Python, Scrapy, Flask, Docker, Kali Linux",
        "difficulty": "advanced",
        "skills": ["python", "flask", "docker", "linux"],
    },
    {
        "title": "Pipeline de données ETL avec visualisation",
        "description": "Système ETL pour collecter, transformer et visualiser des données massives",
        "domain": "DataScience",
        "technologies": "Python, Apache Airflow, Pandas, Streamlit, PostgreSQL",
        "difficulty": "intermediate",
        "skills": ["python", "pandas", "sql", "docker"],
    },
    {
        "title": "Application mobile de gestion de tâches collaborative",
        "description": "App mobile cross-platform avec synchronisation en temps réel et notifications push",
        "domain": "Mobile",
        "technologies": "Flutter, Firebase, Node.js, WebSocket",
        "difficulty": "intermediate",
        "skills": ["flutter", "firebase", "node.js"],
    },
    {
        "title": "Infrastructure CI/CD automatisée",
        "description": "Pipeline DevOps complète avec tests automatisés, containerisation et déploiement continu",
        "domain": "DevOps",
        "technologies": "Docker, Kubernetes, Jenkins, Terraform, AWS",
        "difficulty": "advanced",
        "skills": ["docker", "kubernetes", "aws", "linux"],
    },
    {
        "title": "Système de détection de fake news par NLP",
        "description": "Application utilisant le traitement du langage naturel pour classifier les articles d'actualité",
        "domain": "IA",
        "technologies": "Python, Transformers, BERT, FastAPI, React",
        "difficulty": "advanced",
        "skills": ["python", "machine learning", "fastapi", "react"],
    },
    {
        "title": "Plateforme de gestion de projets agile",
        "description": "Outil de gestion de projets avec tableaux Kanban, sprints et reporting",
        "domain": "Web",
        "technologies": "React, Express.js, MongoDB, Socket.io",
        "difficulty": "beginner",
        "skills": ["react", "node.js", "mongodb"],
    },
    {
        "title": "Système de reconnaissance faciale pour le contrôle d'accès",
        "description": "Application de reconnaissance faciale en temps réel avec caméra pour la sécurité d'accès",
        "domain": "IA",
        "technologies": "Python, OpenCV, TensorFlow, Flask, React",
        "difficulty": "advanced",
        "skills": ["python", "tensorflow", "opencv", "flask"],
    },
]


@router.post("/recommend", response_model=RecommendResponse)
async def recommend_projects(request: RecommendRequest):
    """Generate project recommendations based on user skills and preferences."""
    suggestions = []

    user_skills_lower = [s.lower() for s in request.user_skills]

    for project in PROJECT_DATABASE:
        score = 0.0
        matched = []

        # Skill matching (40% weight)
        project_skills = [s.lower() for s in project["skills"]]
        skill_matches = sum(1 for s in user_skills_lower if any(s in ps for ps in project_skills))
        if project_skills:
            skill_score = skill_matches / len(project_skills)
            score += skill_score * 0.4
            matched = [s for s in request.user_skills if any(s.lower() in ps for ps in project_skills)]

        # Domain matching (30% weight)
        if project["domain"] in request.preferred_domains:
            score += 0.3

        # Difficulty matching (20% weight)
        if project["difficulty"] == request.difficulty:
            score += 0.2
        elif (
            (request.difficulty == "intermediate" and project["difficulty"] == "beginner")
            or (request.difficulty == "advanced" and project["difficulty"] == "intermediate")
        ):
            score += 0.1

        # Base score (10%)
        score += 0.1

        if score >= 0.2:
            reason = f"Correspond à {len(matched)} de vos compétences"
            if project["domain"] in request.preferred_domains:
                reason += f" et au domaine {project['domain']}"

            suggestions.append(ProjectSuggestion(
                title=project["title"],
                description=project["description"],
                domain=project["domain"],
                technologies=project["technologies"],
                difficulty=project["difficulty"],
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
