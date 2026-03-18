# Smart PFE Platform — Walkthrough

## 🚀 Vue d'ensemble du Projet

The **Smart PFE Platform** is now fully implemented as a modern web application designed to help students discover software engineering internship and final year project (PFE) ideas. It leverages a robust microservices architecture separating the frontend, backend, and an intelligent AI service.

---

## 🏗️ Architecture Technique Implémentée

### 1. Backend (Django 6 + Django REST Framework)
- **Authentication (`accounts`)**: Custom [User](file:///c:/Users/hamab/OneDrive/Bureau/smart-pfe-platform/backend/accounts/models.py#5-41) model with roles ([admin](file:///c:/Users/hamab/OneDrive/Bureau/smart-pfe-platform/backend/accounts/models.py#34-37), [student](file:///c:/Users/hamab/OneDrive/Bureau/smart-pfe-platform/backend/accounts/models.py#38-41)), secured with standard JWT (JSON Web Tokens). Includes endpoints for registration, login, and profile management.
- **Projects Catalog ([projects](file:///c:/Users/hamab/OneDrive/Bureau/smart-pfe-platform/backend/projects/admin.py#29-32))**: Comprehensive CRUD for projects, skills mapping, and favorite management. Implements domain and difficulty filtering.
- **Conversations (`conversations`)**: Stores chat history and messages between users and the AI assistant. Acts as a proxy to seamlessly route user messages to the AI microservice.
- **Documents (`documents`)**: Allows users to upload their CVs and project requirement documents (PDF, DOCX, TXT) for AI analysis.
- **Recommendations (`recommendations`)**: Matches user skills with project requirements to generate personalized suggestions and notifications.
- **Database**: Configured for PostgreSQL (defaulting to SQLite for local development). 
- **Settings**: Fully configured CORS (allowing frontend cross-origin requests), static/media file handling, and REST framework permissions.

### 2. AI Microservice (FastAPI + LLM Providers)
- **Chatbot Endpoint (`/api/chat`)**: Integrated with Google Gemini API (fallback to OpenAI and local logic) to provide intelligent project suggestions based on user profiles and conversation context.
- **Document Analysis (`/api/analyze`)**: Analyzes uploaded text (e.g., CVs) to automatically extract technical skills and suggest relevant domains.
- **Recommendation Engine (`/api/recommend`)**: Implements a sophisticated scoring algorithm that weights user skills, preferred domains, and difficulty levels against a detailed project database to surface the best PFE matches.
- **CORS Configured**: Allows seamless communication from the main backend or UI.

### 3. Frontend (React 19)
- **Design System & UI**: Created a premium, glassmorphism-inspired dark theme ([index.css](file:///c:/Users/hamab/OneDrive/Bureau/smart-pfe-platform/frontend/src/index.css)) with responsive grids, interactive micro-animations, and modern typography (Inter).
- **Authentication Layer**: Context-based auth provider handling login/register flows, role management (admin vs. student), and automatic JWT token refreshing via Axios interceptors.
- **Pages Implemented**:
  - **Auth**: Animated Login and Register pages.
  - **Student Dashboard**: Real-time stats, fast action links, and recent tailored projects.
  - **AI Chatbot**: A rich chat interface with message bubbles, typing indicators, markdown rendering for technical responses, and quick suggestion chips.
  - **Project Catalog**: Interactive grid with search functionality, domain filters, and favorite toggling.
  - **Upload Station**: Drag-and-drop document upload interface to feed the AI context about the student.
  - **Favorites**: Personalized list of bookmarked projects.
  - **Admin Dashboard**: Comprehensive statistics, domain distribution charts, user management, and project validation panels.
- **Routing**: Protected routes ensuring students and admins only see what they have access to via React Router v6+.

---

## 🛠️ Validation & Prochaines Étapes

1. **Dépendances**: All Python requirements ([backend/requirements.txt](file:///c:/Users/hamab/OneDrive/Bureau/smart-pfe-platform/backend/requirements.txt), [ai-service/requirements.txt](file:///c:/Users/hamab/OneDrive/Bureau/smart-pfe-platform/ai-service/requirements.txt)) and Node.js packages ([frontend/package.json](file:///c:/Users/hamab/OneDrive/Bureau/smart-pfe-platform/frontend/package.json)) have been configured.
2. **Exécution Local** (When Node.js is available):
   - **Backend**: `cd backend && python manage.py runserver 8000`
   - **AI Service**: `cd ai-service && uvicorn main:app --reload --port 8001`
   - **Frontend**: `cd frontend && npm install && npm start`
3. **À faire par l'utilisateur**: 
   - Add the necessary `GEMINI_API_KEY` and `OPENAI_API_KEY` to an `.env` file in the `ai-service` folder.
   - Run Django migrations to initialize the database: `python manage.py makemigrations` followed by `python manage.py migrate`.

The platform is now feature-complete on the codebase side and ready for execution and end-to-end user testing! 🎉
