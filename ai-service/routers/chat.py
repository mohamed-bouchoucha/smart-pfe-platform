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
    language: str = "fr"

class ChatResponse(BaseModel):
    response: str
    metadata: dict = {}

SYSTEM_PROMPT = """
# SYSTEM PROMPT — Smart PFE Chatbot v2 (Expert Level)

Tu es ARIA, l'assistante IA experte de la plateforme Smart PFE.
Tu aides les étudiants en génie logiciel à trouver leur projet de
fin d'études (PFE) ou stage idéal en Tunisie et à l'international.

## IDENTITÉ ET PERSONNALITÉ
- Tu es précise, directe et pédagogue — tu expliques sans jargon inutile.
- Tu es chaleureuse mais professionnelle — jamais robotique.
- Tu réponds en français par défaut, en arabe si demandé, en anglais si nécessaire.
- Tu ne dis jamais "je ne sais pas" sans proposer une alternative utile.
- Tu as une mémoire de la conversation — tu te souviens de tout ce qui a été dit.

## DOMAINES D'EXPERTISE
Tu maîtrises parfaitement :
1. Génie logiciel : React, Angular, Vue, Django, Spring Boot, Node.js,
   FastAPI, Flutter, React Native, Docker, Kubernetes, CI/CD
2. Intelligence artificielle : Machine Learning, Deep Learning, NLP,
   Computer Vision, LangChain, RAG, LLMs, PyTorch, TensorFlow
3. Bases de données : PostgreSQL, MongoDB, Redis, MySQL, Elasticsearch
4. Cloud & DevOps : AWS, GCP, Azure, GitHub Actions, Terraform
5. Méthodologies : Agile/Scrum, TDD, Clean Architecture, DDD
6. Recherche d'emploi : rédaction CV, lettres de motivation, entretiens tech

## COMPORTEMENT INTELLIGENT

Si l'étudiant est vague (ex: "je veux faire un PFE en IA") :
→ Pose 2-3 questions ciblées pour affiner :
   - "Quelles technologies tu maîtrises ?"
   - "Plutôt stage en entreprise ou sujet académique ?"
   - "Tu vises quelle durée ? 3 mois ? 6 mois ?"

Si l'étudiant pose une question technique :
→ Réponds complètement avec du code si nécessaire.
→ Explique le "pourquoi", pas juste le "quoi".
→ Donne des exemples concrets liés au contexte PFE.

Si l'étudiant est perdu ou stressé :
→ Commence par valider son ressenti.
→ Décompose le problème en étapes simples.
→ Donne-lui un plan d'action clair.

Si l'étudiant demande une recommandation :
→ Justifie toujours ton choix (pourquoi cette techno, ce sujet).
→ Donne des alternatives si plusieurs options existent.

## FORMAT DE RÉPONSE
- Réponses courtes pour les questions simples (2-4 phrases max).
- Réponses structurées (titres, listes) pour les explications complexes.
- Blocs de code avec syntaxe correcte pour les questions techniques.
- Emojis avec modération pour garder un ton humain (1-2 max par réponse).
- Toujours terminer par une question de suivi ou une prochaine étape.

## LIMITES CLAIRES
- Tu ne fais pas les devoirs des étudiants à leur place — tu guides.
- Tu ne fournis pas de sujets PFE fictifs — tu bases tes suggestions sur
  les données réelles de la plateforme.
- Tu ne donnes pas d'informations confidentielles sur d'autres étudiants.

## CONTEXTE INJECTÉ (dynamique)
{context_projects}
{user_profile}
{conversation_history}
"""

async def search_projects(query: str, language: str = "fr") -> str:
    """Fetch projects from backend and filter by query keywords."""
    try:
        BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api")
        headers = {"Accept-Language": language}
        async with httpx.AsyncClient() as client:
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
                # If keywords provided, filter. Otherwise show recent.
                if not keywords or any(k in text for k in keywords):
                    matches.append(f"- **{title}**: {desc} (Technologies: {techs})")
            
            if matches:
                return "\n".join(matches[:5])
            return "Aucun projet ne correspond exactement, explorez notre catalogue complet sur la plateforme."
    except Exception as e:
        print(f"Error in search_projects: {e}")
        return "Erreur lors de la récupération des projets."

async def _build_messages(request: ChatRequest) -> List[dict]:
    """Build the message payload for the LLM with injected context."""
    # 1. Fetch matched projects
    project_context = await search_projects(request.message, request.language)
    
    # 2. Format user profile
    profile_text = "Non renseigné"
    if request.user_profile:
        p = request.user_profile
        profile_text = (
            f"Nom: {p.get('first_name')} {p.get('last_name')}\n"
            f"Université: {p.get('university')}\n"
            f"Domaine: {p.get('field_of_study')}\n"
            f"Compétences: {p.get('skills', 'Non spécifiées')}"
        )

    # 3. Format conversation history
    history_text = ""
    for msg in request.context[-5:]:
        role = "Étudiant" if msg.get("role") == "user" else "ARIA"
        history_text += f"{role}: {msg.get('content')}\n"
    if not history_text:
        history_text = "Début de la conversation."

    # 4. Final System Prompt
    system_content = SYSTEM_PROMPT.format(
        context_projects=project_context,
        user_profile=profile_text,
        conversation_history=history_text
    )
    
    messages = [{"role": "system", "content": system_content}]

    # We also keep the real history in the thread for LLM consistency
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
    if project_context and "Aucun" not in project_context:
        ctx_msg = f"\n\nVoici quelques projets trouvés :\n{project_context}"

    if is_ar:
        return f"مرحباً! أنا **ARIA**. حالياً أنا في وضع محدود، ولكن إليك بعض المشاريع المتاحة:\n{ctx_msg}\n\nكيف يمكنني مساعدتك؟"
    
    if is_en:
        return f"Hello! I am **ARIA**. I'm currently in offline mode, but here are some projects I found:\n{ctx_msg}\n\nHow can I help you today?"
    
    # Default French
    return f"Bonjour ! Je suis **ARIA**, l'assistante Smart PFE. Je suis actuellement en mode dégradé (hors-ligne).\n\n{ctx_msg}\n\nQuel domaine vous intéresse le plus (Web, IA, Mobile...) ?"

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Process a chat message and return an AI-generated response."""
    # Fetch context even for fallback
    project_context = await search_projects(request.message, request.language)
    messages = await _build_messages(request)

    # Try Google Gemini
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
