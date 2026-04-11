import os
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: List[dict] = []
    user_profile: Optional[dict] = None
    language: str = "fr"

class ChatResponse(BaseModel):
    response: str
    metadata: dict = {}

class ApplicationRequest(BaseModel):
    project_title: str
    project_domain: str
    project_description: str
    required_skills: str
    supervisor_name: str
    supervisor_department: str
    open_slots: int
    user_profile: dict
    student_motivation: str = ""
    language: str = "fr"

ARIA_SYSTEM_PROMPT = """
You are ARIA (Adaptive Recommendation & Intelligent Assistant), the AI guide of the Smart PFE Platform — a system that helps Tunisian software engineering students find and apply for End-of-Studies Projects (PFE) and internships.

## Your Identity
- Name: ARIA v2
- Tone: Warm, precise, encouraging. You speak like a knowledgeable senior peer, not a corporate chatbot.
- Language: Respond in the same language the student uses. Support Arabic, French, and English seamlessly. If the student mixes languages, mirror their style.
- Never mention that you are built on Gemini or any underlying model. You are ARIA.

## Student Context (injected at runtime)
You always have access to the following student profile:
- Full name: {student_name}
- Academic level: {academic_level}
- Declared skills: {skills_list}
- Completed courses: {courses_list}
- Previously viewed projects: {viewed_projects}
- Saved/bookmarked projects: {saved_projects}
- Active applications: {active_applications}
- Skill gap reports already generated: {gap_reports}

## Your Capabilities
1. **Project Discovery**: Help students find relevant PFE projects from the catalog by understanding their goals, not just their keywords.
2. **Skill Gap Analysis**: When a student asks about a specific project, compare their skills to the project requirements and explain gaps honestly but constructively.
3. **Application Guidance**: Walk students through how to write a strong motivation letter, prepare for interviews with supervisors, and structure their technical proposal.
4. **Learning Paths**: When a skill gap exists, suggest concrete, free learning resources (courses, docs, GitHub repos) tailored to the missing skill.
5. **Platform Navigation**: Help students understand how to use the Kanban tracker, upload documents, or interpret their match scores.

## Behavioral Rules
- Always personalize your response using the student's actual name and profile. Never give generic advice.
- If you recommend a project, always explain WHY it matches this specific student's profile.
- Never fabricate project details, supervisor names, or deadlines. If you don't know, say so and guide the student to check the catalog.
- Keep responses concise. Use bullet points only when listing 3+ items. Prefer conversational prose.
- If the student seems discouraged or stressed, acknowledge it briefly before providing help.
- Do not discuss topics unrelated to PFE projects, internships, academic skills, or the platform.

## Available Projects
{context_projects}

## Conversation History
{conversation_history}
"""

APPLICATION_PROMPT = """
You are ARIA, helping {student_name} prepare a strong application for the following PFE project.

## Target Project
- Title: {project_title}
- Domain: {project_domain}
- Description: {project_description}
- Required skills: {required_skills}
- Supervisor: {supervisor_name}, {supervisor_department}
- Open slots: {open_slots}

## Student Profile
- Academic level: {academic_level}
- University: {university}
- Skills: {skills_list}
- Relevant projects/experience: {student_experience}
- Motivation (if provided by student): {student_motivation}

## Task
Generate a complete application package containing:

### 1. Motivation Letter (French, formal academic tone)
- Length: 3 short paragraphs (introduction, fit & value, conclusion)
- Must reference the project title and supervisor name
- Must highlight 2–3 of the student's most relevant skills with concrete evidence
- Must end with a professional closing

### 2. Key Talking Points for Supervisor Meeting
- 5 bullet points the student should bring up when first meeting {supervisor_name}
- Include 1 technical question about the project that shows depth of interest

### 3. Technical Proposal Outline
A brief structured outline (not full content) the student can expand into a 2-page technical proposal:
- Problem statement
- Proposed approach
- Technologies to use (aligned with student skills)
- Expected deliverables
- Timeline (12-week PFE skeleton)

### 4. Application Checklist
What documents and steps the student needs to complete on the platform before submitting.

Keep the tone professional but human. Remind the student that this is a starting point and they should personalize it further.
"""

def get_llm(temperature: float = 0.6):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-gemini-api-key-here":
        return None
    return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=temperature, google_api_key=api_key)

async def search_projects(query: str, language: str = "fr") -> str:
    """Fetch projects from backend and filter by query keywords."""
    try:
        BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")
        headers = {"Accept-Language": language}
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BACKEND_URL}/projects/", headers=headers)
            if response.status_code != 200:
                return "Aucun projet spécifique trouvé pour le moment."
            
            data = response.json()
            projects = data.get("results", []) if isinstance(data, dict) else data
            keywords = [k.lower() for k in query.split() if len(k) > 3]
            
            matches = []
            for p in projects:
                title = p.get('title', '')
                desc = p.get('description', '')
                techs = p.get('technologies', '')
                text = f"{title} {desc} {techs}".lower()
                if not keywords or any(k in text for k in keywords):
                    matches.append(f"- **{title}**: {desc} (Technologies: {techs})")
            
            if matches:
                return "\n".join(matches[:5])
            return "Aucun projet ne correspond exactement, explorez notre catalogue complet sur la plateforme."
    except Exception as e:
        print(f"Error in search_projects: {e}")
        return "Erreur lors de la récupération des projets."

def format_history(messages: list[dict]) -> str:
    lines = []
    for msg in messages[-10:]:  # last 10 turns only
        role = "Student" if msg.get("role") == "user" else "ARIA"
        lines.append(f"{role}: {msg.get('content')}")
    return "\n".join(lines)

def _generate_fallback_response(message: str, project_context: str = "") -> str:
    msg = message.lower()
    is_ar = any(c in message for c in "ابتثجحخدذرزسشصضطظعغفقكلمنهوي")
    is_en = any(w in msg for w in ["hello", "help", "project", "find", "ideas", "suggest", "what"])
    ctx_msg = f"\n\nVoici quelques projets trouvés :\n{project_context}" if project_context and "Aucun" not in project_context else ""

    if is_ar:
        return f"مرحباً! أنا **ARIA**. حالياً أنا في وضع محدود، ولكن إليك بعض المشاريع المتاحة:\n{ctx_msg}\n\nكيف يمكنني مساعدتك؟"
    if is_en:
        return f"Hello! I am **ARIA**. I'm currently in offline mode, but here are some projects I found:\n{ctx_msg}\n\nHow can I help you today?"
    
    return f"Bonjour ! Je suis **ARIA**, l'assistante Smart PFE. Je suis actuellement en mode dégradé (hors-ligne).\n\n{ctx_msg}\n\nQuel domaine vous intéresse le plus ?"

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    project_context = await search_projects(request.message, request.language)
    
    llm = get_llm(temperature=0.6)
    if not llm:
        return ChatResponse(
            response=_generate_fallback_response(request.message, project_context),
            metadata={"provider": "fallback"}
        )

    # Format user profile vars
    p = request.user_profile or {}
    student_name = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip() or "Étudiant"
    academic_level = p.get('academic_level', p.get('field_of_study', 'Non spécifié'))
    skills_list = p.get('skills', 'Non spécifiées')

    history_text = format_history(request.context)
    if not history_text:
        history_text = "Début de la conversation."

    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", ARIA_SYSTEM_PROMPT),
            ("human", "{user_message}")
        ])
        chain = prompt | llm
        
        response = chain.invoke({
            "student_name": student_name,
            "academic_level": academic_level,
            "skills_list": skills_list,
            "courses_list": p.get("courses_list", "Non spécifiés"),
            "viewed_projects": p.get("viewed_projects", "Aucun"),
            "saved_projects": p.get("saved_projects", "Aucun"),
            "active_applications": p.get("active_applications", "Aucune"),
            "gap_reports": p.get("gap_reports", "Aucun"),
            "context_projects": project_context,
            "conversation_history": history_text,
            "user_message": request.message
        })
        
        return ChatResponse(
            response=response.content,
            metadata={"provider": "gemini", "model": "gemini-1.5-pro"}
        )
    except Exception as e:
        print(f"Langchain Gemini error: {e}")
        return ChatResponse(
            response=_generate_fallback_response(request.message, project_context),
            metadata={"provider": "fallback"}
        )

@router.post("/generate-application", response_model=ChatResponse)
async def generate_application(request: ApplicationRequest):
    llm = get_llm(temperature=0.7)
    if not llm:
        return ChatResponse(
            response="Service LLM indisponible.",
            metadata={"provider": "fallback"}
        )

    p = request.user_profile or {}
    student_name = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip() or "Étudiant"
    academic_level = p.get('academic_level', p.get('field_of_study', 'Non spécifié'))
    university = p.get('university', 'Non spécifiée')
    skills_list = p.get('skills', 'Non spécifiées')
    student_experience = p.get('experience', 'Aucune expérience spécifique')

    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", APPLICATION_PROMPT)
        ])
        chain = prompt | llm
        
        response = chain.invoke({
            "student_name": student_name,
            "project_title": request.project_title,
            "project_domain": request.project_domain,
            "project_description": request.project_description,
            "required_skills": request.required_skills,
            "supervisor_name": request.supervisor_name,
            "supervisor_department": request.supervisor_department,
            "open_slots": request.open_slots,
            "academic_level": academic_level,
            "university": university,
            "skills_list": skills_list,
            "student_experience": student_experience,
            "student_motivation": request.student_motivation or "Très motivé pour contribuer à ce beau projet."
        })
        
        return ChatResponse(
            response=response.content,
            metadata={"provider": "gemini", "model": "gemini-1.5-pro"}
        )
    except Exception as e:
        print(f"Langchain Application Generator error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la génération de l'application.")
