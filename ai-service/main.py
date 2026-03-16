"""
Smart PFE Platform — AI Microservice
FastAPI application providing chatbot, document analysis, and recommendation endpoints.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import chat, analyze, recommend

load_dotenv()

app = FastAPI(
    title="Smart PFE Platform — AI Service",
    description="Microservice IA pour le chatbot, l'analyse de documents et les recommandations",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["Chatbot"])
app.include_router(analyze.router, prefix="/api", tags=["Document Analysis"])
app.include_router(recommend.router, prefix="/api", tags=["Recommendations"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-service"}
