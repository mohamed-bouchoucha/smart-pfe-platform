"""
Chatbot Router — Processes user messages and returns AI-generated project suggestions.
"""

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# System prompt for the PFE chatbot
SYSTEM_PROMPT = """Tu es un assistant intelligent spécialisé dans les projets de fin d'études (PFE) et stages en génie logiciel.

Ton rôle est d'aider les étudiants à :
1. Trouver des idées de projets adaptées à leur profil
2. Recommander des technologies pertinentes
3. Définir le scope et les objectifs du projet
4. Proposer une architecture technique

Domaines couverts : Intelligence Artificielle, Développement Web, Mobile, DevOps, Cybersécurité, Data Science, IoT, Cloud Computing.

Règles :
- Réponds toujours en français
- Propose des projets réalistes et réalisables pour un PFE (2-6 mois)
- Adapte la difficulté au niveau de l'étudiant
- Fournis des détails techniques concrets (technologies, architecture, fonctionnalités)
- Si l'étudiant est vague, pose des questions pour mieux comprendre ses besoins

Format de suggestion :
📌 **Titre du projet**
📝 Description courte
🛠️ Technologies : ...
⏱️ Durée estimée : ...
📊 Niveau de difficulté : Débutant / Intermédiaire / Avancé
"""


class ChatRequest(BaseModel):
    message: str
    context: list[dict] = []
    user_profile: dict = {}


class ChatResponse(BaseModel):
    response: str
    metadata: dict = {}


def _build_messages(request: ChatRequest) -> list[dict]:
    """Build the message payload for the LLM."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add user profile context
    profile = request.user_profile
    if profile:
        profile_text = f"""Profil de l'étudiant :
- Nom : {profile.get('name', 'Non renseigné')}
- Université : {profile.get('university', 'Non renseignée')}
- Domaine d'études : {profile.get('field_of_study', 'Non renseigné')}
- Bio : {profile.get('bio', 'Non renseignée')}"""
        messages.append({"role": "system", "content": profile_text})

    # Add conversation history
    for msg in request.context[-20:]:  # Last 20 messages for context window
        role = "user" if msg.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": msg.get("content", "")})

    # Add current message
    messages.append({"role": "user", "content": request.message})
    return messages


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Process a chat message and return an AI-generated response."""
    messages = _build_messages(request)

    # Try Google Gemini first
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Convert messages to Gemini format
            prompt = "\n\n".join([
                f"{'System' if m['role'] == 'system' else 'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
                for m in messages
            ])

            response = model.generate_content(prompt)
            return ChatResponse(
                response=response.text,
                metadata={"provider": "gemini", "model": "gemini-1.5-flash"}
            )
        except Exception as e:
            print(f"Gemini error: {e}")

    # Fallback to OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
            )
            return ChatResponse(
                response=response.choices[0].message.content,
                metadata={"provider": "openai", "model": "gpt-3.5-turbo"}
            )
        except Exception as e:
            print(f"OpenAI error: {e}")

    # Fallback response if no API key
    return ChatResponse(
        response=_generate_fallback_response(request.message),
        metadata={"provider": "fallback"}
    )


def _generate_fallback_response(message: str) -> str:
    """Generate a basic response when no LLM API is available."""
    message_lower = message.lower()

    if any(w in message_lower for w in ["ia", "intelligence artificielle", "machine learning", "deep learning"]):
        return """Voici quelques idées de PFE en **Intelligence Artificielle** :

📌 **Système de recommandation intelligent**
📝 Développer un moteur de recommandation basé sur le NLP et le filtrage collaboratif
🛠️ Technologies : Python, TensorFlow, Flask, React
⏱️ Durée : 3 mois | 📊 Intermédiaire

📌 **Chatbot intelligent pour le service client**
📝 Concevoir un assistant conversationnel capable de comprendre le langage naturel
🛠️ Technologies : Python, Transformers, FastAPI, React
⏱️ Durée : 3 mois | 📊 Avancé

📌 **Détection de fraude par ML**
📝 Système de détection d'anomalies dans les transactions financières
🛠️ Technologies : Python, Scikit-learn, Pandas, Streamlit
⏱️ Durée : 2 mois | 📊 Intermédiaire

Quel projet vous intéresse le plus ? Je peux vous donner plus de détails."""

    if any(w in message_lower for w in ["web", "site", "application web", "frontend"]):
        return """Voici quelques idées de PFE en **Développement Web** :

📌 **Plateforme e-learning interactive**
📝 Application web complète avec vidéos, quiz et certificats
🛠️ Technologies : React, Django, PostgreSQL, WebSocket
⏱️ Durée : 3 mois | 📊 Intermédiaire

📌 **Marketplace de services freelance**
📝 Plateforme de mise en relation freelancers/clients avec paiement intégré
🛠️ Technologies : Next.js, Node.js, Stripe, MongoDB
⏱️ Durée : 3 mois | 📊 Avancé

📌 **Dashboard de monitoring en temps réel**
📝 Interface de visualisation de données avec graphiques en temps réel
🛠️ Technologies : React, D3.js, WebSocket, Express
⏱️ Durée : 2 mois | 📊 Intermédiaire

Dites-moi lequel vous attire, et je détaillerai le cahier des charges !"""

    if any(w in message_lower for w in ["cybersécurité", "sécurité", "pentest"]):
        return """Voici quelques idées de PFE en **Cybersécurité** :

📌 **Scanner de vulnérabilités web**
📝 Outil automatisé de détection de failles OWASP Top 10
🛠️ Technologies : Python, Scrapy, Flask, Docker
⏱️ Durée : 3 mois | 📊 Avancé

📌 **Système de détection d'intrusion (IDS)**
📝 Monitoring réseau avec machine learning pour détecter les attaques
🛠️ Technologies : Python, Scapy, TensorFlow, ELK Stack
⏱️ Durée : 3 mois | 📊 Avancé

Souhaitez-vous approfondir l'un de ces projets ?"""

    return """Bonjour ! 👋 Je suis l'assistant **Smart PFE**.

Je peux vous aider à trouver des idées de projets de PFE adaptées à votre profil. Pour mieux vous recommander des projets, dites-moi :

1. 🎯 **Quel domaine** vous intéresse ? (IA, Web, Mobile, DevOps, Cybersécurité, Data Science...)
2. 🛠️ **Quelles technologies** maîtrisez-vous ?
3. ⏱️ **Quelle durée** pour votre stage ? (1, 2, 3, ou 6 mois)
4. 📊 **Quel niveau** de difficulté souhaitez-vous ?

N'hésitez pas à me poser vos questions !"""
