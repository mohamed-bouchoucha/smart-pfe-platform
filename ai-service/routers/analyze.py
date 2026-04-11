import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

router = APIRouter()

class AnalyzeRequest(BaseModel):
    text: str
    doc_type: str = "cv"
    user_profile: dict = {}

class AnalyzeResponse(BaseModel):
    summary: str
    extracted_skills: List[str]
    suggested_domains: List[str]
    confidence: float
    raw_data: Optional[dict] = None

CV_ANALYSIS_PROMPT = """
You are ARIA, analyzing a student's CV for the Smart PFE Platform.

## Uploaded Document
{extracted_cv_text}

## Task
Extract and structure the following information from the CV text:

### 1. Detected Skills
List all technical skills mentioned (programming languages, frameworks, tools, cloud platforms, databases).
For each, infer a proficiency level based on context clues (years mentioned, project complexity, certifications):
- Beginner: mentioned once, no project context
- Intermediate: used in 1–2 projects
- Advanced: multiple projects, certifications, or leadership

### 2. Academic Background
- Degree and field
- Institution
- Graduation year or current year
- Notable courses or GPA if mentioned

### 3. Project Experience
For each project mentioned, extract:
- Project name/description
- Technologies used
- Role (solo, team lead, contributor)
- Outcome or result if mentioned

### 4. Internship / Work Experience
List past internships with company, duration, and technologies used.

### 5. Profile Summary
Write a 3-sentence professional summary of this student as if you were recommending them to a supervisor. Be specific — use actual details from the CV.

### 6. Platform Profile Update Suggestions
List up to 5 skills that should be added to the student's platform profile based on the CV, which may not have been declared yet.

Return the result as a valid JSON object with keys:
skills, academic_background, projects, experience, summary, suggested_profile_updates

No markdown. JSON only.
"""

def get_llm(temperature: float = 0.1):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-gemini-api-key-here":
        return None
    return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=temperature, google_api_key=api_key)

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_document(request: AnalyzeRequest):
    """Analyze a document and extract relevant information using LLM."""
    if request.doc_type != "cv":
        # Simplified handling for non-CV docs
        return AnalyzeResponse(
            summary=f"Document de type {request.doc_type} analysé. L'analyse IA détaillée est réservée aux CV.",
            extracted_skills=[],
            suggested_domains=[],
            confidence=0.5
        )

    llm = get_llm(temperature=0.1)
    if not llm:
        # Fallback keyword extraction
        text_lower = request.text.lower()
        skill_keywords = ['python', 'react', 'java', 'sql', 'docker', 'machine learning', 'javascript']
        extracted = [s for s in skill_keywords if s in text_lower]
        return AnalyzeResponse(
            summary="Analyse de base effectuée (mode hors-ligne).",
            extracted_skills=extracted,
            suggested_domains=["Web", "IA"] if extracted else [],
            confidence=0.6,
            raw_data={"skills": extracted}
        )

    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", CV_ANALYSIS_PROMPT)
        ])
        parser = JsonOutputParser()
        chain = prompt | llm | parser

        result = chain.invoke({
            "extracted_cv_text": request.text
        })
        
        # Parse the structured JSON back into the standard response
        skills_data = result.get("skills", [])
        extracted_skills = []
        if isinstance(skills_data, list):
            for s in skills_data:
                if isinstance(s, dict) and "skill" in s:
                    extracted_skills.append(s["skill"])
                elif isinstance(s, str):
                    extracted_skills.append(s)
        
        # Basic domain inferencing from skills
        domains = []
        text_lower = request.text.lower()
        if "machine learning" in text_lower or "python" in text_lower or "tensorflow" in text_lower:
            domains.append("IA")
        if "react" in text_lower or "web" in text_lower or "django" in text_lower or "html" in text_lower:
            domains.append("Web")
        if "docker" in text_lower or "kubernetes" in text_lower:
            domains.append("DevOps")

        return AnalyzeResponse(
            summary=result.get("summary", "CV Analysé avec succès."),
            extracted_skills=extracted_skills,
            suggested_domains=domains if domains else ["Génie Logiciel"],
            confidence=0.9,
            raw_data=result
        )

    except Exception as e:
        print(f"Langchain CV Analysis error: {e}")
        return AnalyzeResponse(
            summary="Erreur lors de l'analyse du CV.",
            extracted_skills=[],
            suggested_domains=[],
            confidence=0.0
        )
