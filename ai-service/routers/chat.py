import os
import httpx
import google.generativeai as genai
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: List[dict] = []
    user_profile: Optional[dict] = None

class ChatResponse(BaseModel):
    response: str
    metadata: dict = {}

SYSTEM_PROMPT = """
You are the Smart PFE Assistant, a premium AI counselor for university students.
Your goal is to help students find the perfect Final Year Project (PFE) based on their skills and interests.

CORE CAPABILITIES:
1. **Multilingualism**: Respond in the same language as the user (Français, English, or Arabic). Use a professional and encouraging tone.
2. **Project Expert**: Use the provided project context to suggest REAL projects from our database.
3. **Guidance**: If the user is unsure, ask about their favorite technologies or domains.

INTERACTIVITY:
- Use Markdown for formatting.
- If you suggest a project from the context, mention its title clearly.
- If you find no matching project, propose a creative new one and mark it as (Nouveau).
"""

async def search_projects(query: str) -> str:
    """Fetch projects from backend and filter by query keywords."""
    try:
        BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/projects/")
            if response.status_code != 200:
                return ""
            
            data = response.json()
            projects = data.get("results", []) if isinstance(data, dict) else data
            keywords = [k.lower() for k in query.split() if len(k) > 3]
            
            matches = []
            for p in projects:
                title = p.get('title', '')
                desc = p.get('description', '')
                techs = p.get('technologies', '')
                text = f"{title} {desc} {techs}".lower()
                if any(k in text for k in keywords):
                    matches.append(f"- **{title}**: {desc} (Tech: {techs})")
            
            if matches:
                return "\nPROJETS RÉELS DISPONIBLES DANS NOTRE BASE:\n" + "\n".join(matches[:3])
            return ""
    except Exception as e:
        print(f"Error in search_projects: {e}")
        return ""

async def _build_messages(request: ChatRequest) -> List[dict]:
    """Build the message payload for the LLM."""
    project_context = await search_projects(request.message)
    
    system_content = SYSTEM_PROMPT
    if project_context:
        system_content += f"\n\n{project_context}"
    
    messages = [{"role": "system", "content": system_content}]

    # Add user profile context
    if request.user_profile:
        p = request.user_profile
        profile_text = f"Infos Étudiant: Nom={p.get('first_name')} {p.get('last_name')}, Univ={p.get('university')}, Études={p.get('field_of_study')}"
        messages.append({"role": "system", "content": profile_text})

    # Add conversation history
    for msg in request.context[-10:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

    # Add current message
    messages.append({"role": "user", "content": request.message})
    return messages

def _generate_fallback_response(message: str, project_context: str = "") -> str:
    """Enhanced multilingual fallback using available project context."""
    msg = message.lower()
    
    # Language detection
    is_ar = any(c in message for c in "ابتثجحخدذرزسشصضطظعغفقكلمنهوي")
    is_en = any(w in msg for w in ["hello", "help", "project", "find", "ideas", "suggest", "what"])

    # Build context string
    ctx_msg = ""
    if project_context:
        ctx_msg = f"\n\n{project_context}"

    if is_ar:
        return f"مرحباً! أنا مساعد **Smart PFE**. حالياً أنا في وضع محدود (Offline)، ولكن وجدت لك هذه المشاريع في قاعدتنا:\n{ctx_msg}\n\nكيف يمكنني مساعدتك أكثر؟"
    
    if is_en:
        return f"Hello! I am the **Smart PFE** assistant. I'm currently in offline mode, but I found these real projects for you:\n{ctx_msg}\n\nWhat domain would you like to explore next?"
    
    # Default French
    return f"Bonjour ! Je suis l'assistant **Smart PFE**. (Mode hors-ligne).\n\nVoici des projets réels correspondants à votre recherche :\n{ctx_msg}\n\nQuel domaine vous intéresse le plus (IA, Web, Mobile...) ?"

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Process a chat message and return an AI-generated response."""
    # Fetch context even for fallback
    project_context = await search_projects(request.message)
    messages = await _build_messages(request)

    # Try Google Gemini first
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key != "your-gemini-api-key-here":
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            contents = []
            for m in messages:
                # Gemini roles are strictly 'user' or 'model'
                role = "user" if m["role"] in ["user", "system"] else "model"
                contents.append({"role": role, "parts": [{"text": m["content"]}]})

            response = model.generate_content(contents)
            return ChatResponse(
                response=response.text,
                metadata={"provider": "gemini", "model": "gemini-1.5-flash"}
            )
        except Exception as e:
            print(f"Gemini error: {e}")

    # Final fallback if no API keys working
    return ChatResponse(
        response=_generate_fallback_response(request.message, project_context),
        metadata={"provider": "fallback"}
    )
