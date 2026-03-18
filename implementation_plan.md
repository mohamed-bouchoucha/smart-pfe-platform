# Smart PFE Platform — Plan d'Implémentation

Plateforme web intelligente pour aider les étudiants à trouver des idées de PFE/Stage en génie logiciel. Stack : **React 19 + Django 6 + DRF + FastAPI (AI) + PostgreSQL**.

---

## 1️⃣ Diagramme UML — Class Diagram Complet

```mermaid
classDiagram
    direction TB

    class User {
        +int id
        +string email
        +string username
        +string first_name
        +string last_name
        +string password
        +enum role : admin|student
        +string university
        +string field_of_study
        +string skills
        +string bio
        +datetime date_joined
        +bool is_active
        +register()
        +login()
        +updateProfile()
        +getRecommendations()
    }

    class Project {
        +int id
        +string title
        +text description
        +string domain
        +string technologies
        +enum difficulty : beginner|intermediate|advanced
        +enum duration : 1month|2months|3months|6months
        +enum status : draft|validated|rejected
        +string company_name
        +int supervisor_id
        +datetime created_at
        +datetime updated_at
        +validate()
        +reject()
        +getMatchingStudents()
    }

    class Conversation {
        +int id
        +int user_id
        +string title
        +datetime created_at
        +datetime updated_at
        +bool is_active
        +getMessages()
        +summarize()
        +archive()
    }

    class Message {
        +int id
        +int conversation_id
        +enum sender : user|assistant
        +text content
        +json metadata
        +datetime timestamp
        +getTokenCount()
    }

    class Document {
        +int id
        +int user_id
        +string filename
        +string file_path
        +enum doc_type : cv|cahier_charges|report|other
        +int file_size
        +string mime_type
        +text extracted_text
        +bool is_analyzed
        +datetime uploaded_at
        +upload()
        +analyze()
        +extractText()
        +delete()
    }

    class Favorite {
        +int id
        +int user_id
        +int project_id
        +datetime saved_at
        +save()
        +remove()
    }

    class Recommendation {
        +int id
        +int user_id
        +int project_id
        +float score
        +string reason
        +json matched_skills
        +datetime generated_at
        +generate()
        +refresh()
    }

    class Skill {
        +int id
        +string name
        +string category
        +getRelatedProjects()
    }

    class Notification {
        +int id
        +int user_id
        +string title
        +text message
        +enum type : info|success|warning
        +bool is_read
        +datetime created_at
        +markAsRead()
    }

    class AuditLog {
        +int id
        +int user_id
        +string action
        +string resource
        +json details
        +string ip_address
        +datetime timestamp
    }

    User "1" --> "*" Conversation : starts
    User "1" --> "*" Document : uploads
    User "1" --> "*" Favorite : saves
    User "1" --> "*" Recommendation : receives
    User "*" --> "*" Skill : has
    User "1" --> "*" Notification : receives
    User "1" --> "*" AuditLog : generates
    Conversation "1" --> "*" Message : contains
    Project "1" --> "*" Favorite : saved_in
    Project "1" --> "*" Recommendation : recommended_in
    Project "*" --> "*" Skill : requires
```

---

## 2️⃣ Diagramme de Base de Données (ER Diagram)

```mermaid
erDiagram
    USER {
        int id PK
        varchar email UK
        varchar username UK
        varchar password_hash
        varchar first_name
        varchar last_name
        varchar role "admin | student"
        varchar university
        varchar field_of_study
        text skills_description
        text bio
        boolean is_active
        timestamp date_joined
        timestamp last_login
    }

    PROJECT {
        int id PK
        varchar title
        text description
        varchar domain "IA | Web | DevOps | Cybersecurity | DataScience"
        varchar technologies
        varchar difficulty "beginner | intermediate | advanced"
        varchar duration "1month | 2months | 3months | 6months"
        varchar status "draft | validated | rejected"
        varchar company_name
        int created_by FK
        timestamp created_at
        timestamp updated_at
    }

    CONVERSATION {
        int id PK
        int user_id FK
        varchar title
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    MESSAGE {
        int id PK
        int conversation_id FK
        varchar sender "user | assistant"
        text content
        jsonb metadata
        timestamp timestamp
    }

    DOCUMENT {
        int id PK
        int user_id FK
        varchar filename
        varchar file_path
        varchar doc_type "cv | cahier_charges | report | other"
        int file_size_bytes
        varchar mime_type
        text extracted_text
        boolean is_analyzed
        timestamp uploaded_at
    }

    FAVORITE {
        int id PK
        int user_id FK
        int project_id FK
        timestamp saved_at
    }

    RECOMMENDATION {
        int id PK
        int user_id FK
        int project_id FK
        float score
        text reason
        jsonb matched_skills
        timestamp generated_at
    }

    SKILL {
        int id PK
        varchar name UK
        varchar category "language | framework | tool | methodology"
    }

    USER_SKILL {
        int user_id FK
        int skill_id FK
        varchar proficiency "beginner | intermediate | expert"
    }

    PROJECT_SKILL {
        int project_id FK
        int skill_id FK
        boolean is_required
    }

    NOTIFICATION {
        int id PK
        int user_id FK
        varchar title
        text message
        varchar type "info | success | warning"
        boolean is_read
        timestamp created_at
    }

    AUDIT_LOG {
        int id PK
        int user_id FK
        varchar action
        varchar resource
        jsonb details
        varchar ip_address
        timestamp timestamp
    }

    USER ||--o{ CONVERSATION : "starts"
    USER ||--o{ DOCUMENT : "uploads"
    USER ||--o{ FAVORITE : "saves"
    USER ||--o{ RECOMMENDATION : "receives"
    USER ||--o{ NOTIFICATION : "notified"
    USER ||--o{ AUDIT_LOG : "tracked"
    USER ||--o{ USER_SKILL : "has"
    SKILL ||--o{ USER_SKILL : "possessed_by"
    SKILL ||--o{ PROJECT_SKILL : "needed_by"
    PROJECT ||--o{ PROJECT_SKILL : "requires"
    PROJECT ||--o{ FAVORITE : "bookmarked"
    PROJECT ||--o{ RECOMMENDATION : "suggested"
    CONVERSATION ||--o{ MESSAGE : "contains"
    USER ||--o{ PROJECT : "creates"
```

---

## 3️⃣ Architecture Microservices AI — Diagramme Professionnel

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

## 4️⃣ Diagramme de Séquence — Flux Chatbot

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
    LLM-->>AI: Réponse structurée (projets suggérés)
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

## 5️⃣ Diagramme de Cas d'Utilisation

```mermaid
graph LR
    subgraph Actors
        STUDENT["🎓 Étudiant"]
        ADMIN["👨‍💼 Admin"]
        AI_BOT["🤖 ChatBot IA"]
    end

    subgraph Platform["Smart PFE Platform"]
        UC1["S'inscrire / Se connecter"]
        UC2["Chercher des projets"]
        UC3["Discuter avec le Chatbot"]
        UC4["Recevoir des recommandations"]
        UC5["Upload CV / Documents"]
        UC6["Sauvegarder des favoris"]
        UC7["Consulter le Dashboard"]
        UC8["Gérer les utilisateurs"]
        UC9["Valider les projets"]
        UC10["Consulter les statistiques"]
        UC11["Analyser les documents"]
        UC12["Générer des suggestions"]
    end

    STUDENT --> UC1
    STUDENT --> UC2
    STUDENT --> UC3
    STUDENT --> UC4
    STUDENT --> UC5
    STUDENT --> UC6
    STUDENT --> UC7

    ADMIN --> UC1
    ADMIN --> UC8
    ADMIN --> UC9
    ADMIN --> UC10

    AI_BOT --> UC11
    AI_BOT --> UC12
    UC3 --> AI_BOT
    UC5 --> UC11
```

---

## Proposed Changes

### Backend Component

#### [MODIFY] [settings.py](file:///c:/Users/hamab/OneDrive/Bureau/smart-pfe-platform/backend/config/settings.py)
Configure for DRF, JWT auth, CORS, PostgreSQL, Celery, and media file storage.

#### [NEW] `backend/accounts/` — Custom user model, JWT auth views, serializers
#### [NEW] `backend/projects/` — Project CRUD, validation, domain filtering
#### [NEW] `backend/conversations/` — Chat sessions, message storage
#### [NEW] `backend/documents/` — File upload, text extraction
#### [NEW] `backend/recommendations/` — Skill matching, scoring engine
#### [NEW] `backend/requirements.txt` — All Python dependencies

---

### Frontend Component

#### [MODIFY] [package.json](file:///c:/Users/hamab/OneDrive/Bureau/smart-pfe-platform/frontend/package.json)
Add react-router-dom, axios, react-markdown, react-icons, chart.js, framer-motion.

#### [NEW] `frontend/src/components/` — Reusable UI components (Navbar, Sidebar, ChatBubble, ProjectCard, FileUpload)
#### [NEW] `frontend/src/pages/` — Login, Register, Dashboard, Chatbot, Admin, Projects, Upload
#### [NEW] `frontend/src/services/` — API client, auth service, chat service
#### [NEW] `frontend/src/context/` — AuthContext, ChatContext
#### [NEW] [frontend/src/index.css](file:///c:/Users/hamab/OneDrive/Bureau/smart-pfe-platform/frontend/src/index.css) — Design system with premium dark theme

---

### AI Service Component

#### [NEW] `ai-service/main.py` — FastAPI app with /chat, /analyze, /recommend endpoints
#### [NEW] `ai-service/requirements.txt` — fastapi, uvicorn, openai, google-generativeai, chromadb
#### [NEW] `ai-service/services/` — chatbot.py, document_analyzer.py, recommendation_engine.py

---

### Documentation

#### [MODIFY] [README.md](file:///c:/Users/hamab/OneDrive/Bureau/smart-pfe-platform/README.md)
#### [MODIFY] [architecture.md](file:///c:/Users/hamab/OneDrive/Bureau/smart-pfe-platform/docs/architecture.md)
#### [NEW] `docs/database_diagram.md` — ER diagram
#### [NEW] `docs/uml_class_diagram.md` — UML class diagram
#### [NEW] `docs/api_specification.md` — REST API endpoints documentation

---

## 6️⃣ Plan de Réalisation — 3 Semaines

### Semaine 1 : Fondations & Backend Core

| Jour | Tâches |
|------|--------|
| **J1–J2** | Setup PostgreSQL, configurer Django settings, custom User model, JWT auth |
| **J3** | App `projects` — modèles, serializers, vues CRUD, filtres |
| **J4** | App `conversations` + `messages` — API pour le chat |
| **J5** | App `documents` — upload, stockage, extraction de texte |

### Semaine 2 : AI Service & Frontend

| Jour | Tâches |
|------|--------|
| **J6** | FastAPI AI service — endpoint chatbot + intégration Gemini |
| **J7** | Document analyzer + recommendation engine |
| **J8–J9** | Frontend — design system, auth pages, routing, protected routes |
| **J10** | Frontend — Dashboard étudiant, chatbot widget interactif |

### Semaine 3 : Intégration & Polish

| Jour | Tâches |
|------|--------|
| **J11** | Frontend — Admin dashboard, upload pages, favorites |
| **J12** | Intégration complète frontend ↔ backend ↔ AI |
| **J13** | Tests end-to-end, correction de bugs |
| **J14** | Documentation finale, déploiement Docker, présentation |

---

## Verification Plan

### Automated Tests
1. **Backend**: `cd backend && python manage.py test` — unit tests for all Django apps
2. **Frontend**: `cd frontend && npm test` — React Testing Library tests
3. **AI Service**: `cd ai-service && pytest` — FastAPI endpoint tests

### Browser Verification
- Navigate to `http://localhost:3000` and verify the login/register flow
- Test chatbot conversation flow
- Verify admin dashboard with user management
- Test file upload and project browsing

### Manual Verification
- Ask the user to review all Mermaid diagrams rendered in the docs
- Verify the architecture diagram matches the implemented microservices
