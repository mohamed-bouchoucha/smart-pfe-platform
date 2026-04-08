import os
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class ResourceRequest(BaseModel):
    missing_skills: List[str]
    language: str = "fr"

class ResourceResponse(BaseModel):
    recommendations: str
    metadata: dict = {}

@router.post("/recommend-resources", response_model=ResourceResponse)
async def recommend_resources(request: ResourceRequest):
    """Suggest learning resources for missing skills using Gemini."""
    if not request.missing_skills:
        return ResourceResponse(
            recommendations="Bravo ! Vous avez déjà toutes les compétences requises pour ce projet.",
            metadata={"status": "no_gap"}
        )

    skills_list = ", ".join(request.missing_skills)
    prompt = f"""
    En tant qu'expert en orientation académique et technique, suggère des ressources d'apprentissage 
    de haute qualité pour combler les lacunes suivantes en informatique : {skills_list}.
    
    Pour chaque compétence, propose :
    1. Un lien vers la documentation officielle.
    2. Un cours gratuit recommandé (ex: Coursera, edX, YouTube, MDN).
    3. Un conseil pratique pour apprendre rapidement.
    
    Réponds en {request.language}. Utilise le format Markdown avec des titres et des puces.
    Sois encourageant et précis.
    """

    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key != "your-gemini-api-key-here":
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return ResourceResponse(
                recommendations=response.text,
                metadata={"provider": "gemini", "model": "gemini-1.5-flash"}
            )
        except Exception as e:
            print(f"Gemini error in skills cluster: {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de la génération des recommandations.")

    # Fallback response
    fallback = f"### Ressources pour {skills_list}\n\nMalheureusement, le service de recommandation IA est temporairement indisponible. Veuillez consulter la documentation officielle de ces technologies sur Google."
    return ResourceResponse(recommendations=fallback, metadata={"provider": "fallback"})
