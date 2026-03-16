# Smart PFE Platform — Architecture Technique

## Vue d'ensemble

Plateforme web intelligente basée sur une architecture **microservices** avec séparation claire entre le Frontend (React), le Backend (Django/DRF), et le Service IA (FastAPI).

---

## Architecture Microservices

```mermaid
graph TB
    subgraph CLIENT["🖥️ Frontend — React 19"]
        UI["UI Components"]
        ROUTER["React Router v7"]
        STATE["Context API / State"]
        AXIOS["Axios HTTP Client"]
        CHAT_UI["Chatbot Widget"]
    end

    subgraph API_GATEWAY["🔒 API Gateway — Nginx"]
        NGINX["Reverse Proxy / Load Balancer"]
        SSL["TLS/SSL Termination"]
        RATE["Rate Limiting"]
    end

    subgraph BACKEND["⚙️ Backend — Django 6 + DRF"]
        AUTH["Auth Service (JWT)"]
        USERS["Users API"]
        PROJECTS["Projects API"]
        CONV["Conversations API"]
        DOCS["Documents API"]
        RECO["Recommendations API"]
        ADMIN_API["Admin API"]
    end

    subgraph AI_SERVICE["🤖 AI Microservice — FastAPI"]
        CHATBOT["Chatbot Engine"]
        DOC_ANALYZER["Document Analyzer"]
        RECO_ENGINE["Recommendation Engine"]
        NLP["NLP Pipeline"]
        EMBEDDINGS["Embeddings Service"]
    end

    subgraph LLM_PROVIDERS["🧠 LLM Providers"]
        GEMINI["Google Gemini API"]
        OPENAI["OpenAI GPT API"]
        LOCAL_LLM["Local LLM (Ollama)"]
    end

    subgraph DATA["💾 Data Layer"]
        POSTGRES[("PostgreSQL")]
        REDIS[("Redis Cache")]
        MEDIA[("Media Storage (S3/Local)")]
        VECTOR_DB[("Vector Store (ChromaDB)")]
    end

    subgraph INFRA["🔧 Infrastructure"]
        CELERY["Celery Workers"]
        MONITOR["Monitoring (Prometheus)"]
        LOGS["Centralized Logging"]
    end

    UI --> AXIOS
    CHAT_UI --> AXIOS
    AXIOS --> NGINX
    NGINX --> AUTH
    NGINX --> USERS
    NGINX --> PROJECTS
    NGINX --> CONV
    NGINX --> DOCS
    NGINX --> RECO
    NGINX --> ADMIN_API

    AUTH --> POSTGRES
    AUTH --> REDIS
    USERS --> POSTGRES
    PROJECTS --> POSTGRES
    CONV --> POSTGRES
    DOCS --> POSTGRES
    DOCS --> MEDIA
    RECO --> POSTGRES

    CONV --> CHATBOT
    DOCS --> DOC_ANALYZER
    RECO --> RECO_ENGINE

    CHATBOT --> NLP
    CHATBOT --> EMBEDDINGS
    DOC_ANALYZER --> NLP
    RECO_ENGINE --> EMBEDDINGS

    NLP --> GEMINI
    NLP --> OPENAI
    NLP --> LOCAL_LLM
    EMBEDDINGS --> VECTOR_DB

    CELERY --> DOC_ANALYZER
    CELERY --> RECO_ENGINE
    CELERY --> REDIS

    style CLIENT fill:#1a1a2e,stroke:#e94560,color:#fff
    style API_GATEWAY fill:#16213e,stroke:#0f3460,color:#fff
    style BACKEND fill:#0f3460,stroke:#533483,color:#fff
    style AI_SERVICE fill:#533483,stroke:#e94560,color:#fff
    style LLM_PROVIDERS fill:#2d1b69,stroke:#e94560,color:#fff
    style DATA fill:#1a1a2e,stroke:#0f3460,color:#fff
    style INFRA fill:#16213e,stroke:#533483,color:#fff
```

---

## Flux de Communication

```mermaid
sequenceDiagram
    actor Student as 🎓 Student
    participant React as React Frontend
    participant API as Django API
    participant AI as FastAPI AI Service
    participant LLM as Gemini / GPT
    participant DB as PostgreSQL

    Student->>React: Ouvre le chatbot
    React->>API: GET /api/conversations/ (JWT)
    API->>DB: Fetch conversations
    DB-->>API: conversation list
    API-->>React: conversations[]

    Student->>React: Envoie "Je cherche un PFE en IA"
    React->>API: POST /api/conversations/{id}/messages/
    API->>DB: Save user message
    API->>AI: POST /ai/chat {message, context, user_profile}
    AI->>LLM: Prompt enrichi + historique
    LLM-->>AI: Réponse structurée
    AI-->>API: {response, suggestions[], metadata}
    API->>DB: Save assistant message + recommendations
    API-->>React: {message, suggestions[]}
    React-->>Student: Affiche la réponse + cartes de projets

    Student->>React: Clique "Sauvegarder" sur un projet
    React->>API: POST /api/favorites/
    API->>DB: Create favorite
    API-->>React: 201 Created
    React-->>Student: ❤️ Projet sauvegardé!
```

---

## Stack Technique

| Couche | Technologie | Rôle |
|--------|-------------|------|
| Frontend | React 19, React Router 7, Axios, Framer Motion | Interface utilisateur SPA |
| Backend | Django 6, DRF, SimpleJWT | API REST, logique métier |
| AI Service | FastAPI, LangChain, ChromaDB | Chatbot, analyse, recommandations |
| Database | PostgreSQL 16 | Stockage relationnel |
| Cache | Redis | Sessions, cache, file de tâches |
| Task Queue | Celery | Traitement asynchrone |
| LLM | Google Gemini / OpenAI GPT | Génération de langage naturel |
| Reverse Proxy | Nginx | Load balancing, SSL |

---

## Endpoints API Principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/auth/register/` | Inscription |
| POST | `/api/auth/login/` | Connexion (JWT) |
| POST | `/api/auth/token/refresh/` | Rafraîchir le token |
| GET | `/api/users/me/` | Profil utilisateur |
| GET/POST | `/api/projects/` | Lister / créer des projets |
| GET/POST | `/api/conversations/` | Lister / créer des conversations |
| POST | `/api/conversations/{id}/messages/` | Envoyer un message au chatbot |
| POST | `/api/documents/upload/` | Upload de fichiers |
| GET | `/api/recommendations/` | Obtenir des recommandations |
| GET | `/api/favorites/` | Projets favoris |
| GET | `/api/admin/stats/` | Statistiques admin |

---

## Sécurité

- **Authentification** : JWT (access + refresh tokens)
- **Autorisation** : Rôles `admin` / `student` avec permissions DRF
- **CORS** : Configuré pour le frontend uniquement
- **Validation** : Serializers DRF + validation côté client
- **Fichiers** : Validation MIME type + taille maximale
- **Rate Limiting** : Throttling DRF + Nginx
