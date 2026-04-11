import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

router = APIRouter()

class AdminAnalyticsRequest(BaseModel):
    period: str
    total_students: int
    active_applications: int
    total_projects: int
    domain_distribution: str
    supervisor_stats: str
    top_skill_gaps: str
    conversion_rate: float
    avg_match_score: float
    overload_threshold: int = 5

class AdminAnalyticsResponse(BaseModel):
    summary: str
    metadata: dict = {}

ADMIN_ANALYTICS_PROMPT = """
You are ARIA in administrator mode, analyzing platform data for the Smart PFE Platform admin team.

## Platform Statistics (current period: {period})
- Total registered students: {total_students}
- Active applications: {active_applications}
- Projects posted: {total_projects}
- Domain distribution: {domain_distribution}
- Supervisor workload: {supervisor_stats}
- Most common skill gaps detected: {top_skill_gaps}
- Application conversion rate: {conversion_rate}%
- Average match score across all students: {avg_match_score}

## Task
Generate a concise executive summary (max 200 words) covering:
1. Platform health — is engagement healthy?
2. Top 2 actionable insights from the data
3. One recommended action for the admin team this week

Then generate:
- A list of supervisors who are overloaded (more than {overload_threshold} applications) and need support
- A list of projects with 0 applications that may need better visibility or updated descriptions
- The top 3 skill gaps on the platform and suggested partnerships or workshops to address them

Keep the tone professional and data-driven. Avoid speculation beyond what the data supports.
"""

def get_llm(temperature: float = 0.1):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-gemini-api-key-here":
        return None
    return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=temperature, google_api_key=api_key)

@router.post("/admin-analytics", response_model=AdminAnalyticsResponse)
async def generate_admin_analytics(request: AdminAnalyticsRequest):
    """Generate NLP insights for admin dashboard."""
    llm = get_llm(temperature=0.1)
    if not llm:
        return AdminAnalyticsResponse(
            summary="Service IA hors-ligne. Impossible de générer l'analyse.",
            metadata={"provider": "fallback"}
        )

    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", ADMIN_ANALYTICS_PROMPT)
        ])
        chain = prompt | llm
        
        response = chain.invoke(request.dict())
        
        return AdminAnalyticsResponse(
            summary=response.content,
            metadata={"provider": "gemini", "model": "gemini-1.5-pro"}
        )
    except Exception as e:
        print(f"Langchain Admin Analytics error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la génération de l'analyse.")
