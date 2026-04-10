# Smart PFE Platform

[![License: Academic](https://img.shields.io/badge/License-Academic-blue.svg)](LICENSE)
[![Microservices](https://img.shields.io/badge/Architecture-Microservices-orange.svg)]()
[![AI-Powered](https://img.shields.io/badge/AI-Powered-purple.svg)]()

A comprehensive, AI-driven orchestrator designed to streamline the discovery and management of End-of-Studies Projects (PFE) and internships for software engineering students.

## Overview

Finding the right PFE project is often a fragmented process. Students struggle with skill misalignment, while supervisors are overwhelmed by manual application tracking. 

**Smart PFE** solves this by acting as an intelligent bridge. It combines a robust management backend with an AI-first approach to project matching, skill analysis, and recruitment pipeline automation.

---

## Features

### 🚀 Core Workflow
- **Intelligent Discovery**: Advanced multi-factor search and filtering for project catalogs.
- **Application Pipeline**: Kanban-based tracking system for students to monitor their journey from initial interest to final acceptance.
- **Document Management**: Centralized repository for CVs, proposals, and technical specifications.

### 🧠 AI & Analytics (Advanced)
- **ARIA v2 Assistant**: A context-aware chatbot that understands student profiles and conversation history to provide hyper-personalized project suggestions.
- **Skill Gap Analyzer**: Interactive radar visualizations (Chart.js) comparing student skills with project requirements.
- **Learning Resource Generator**: Automated AI suggestions for learning paths based on detected skill gaps.
- **Signal-Driven Notifications**: Real-time platform alerts triggered by project status changes or administrative actions.

### 🛠 Administration & Ops
- **Admin Command Center**: High-level statistics on platform usage, domain distribution, and supervisor workload.
- **Role-Based Access Control (RBAC)**: Fine-grained permissions for Students, Supervisors, and Administrators.

---

## Tech Stack

- **Backend**: Django 6.0, Django REST Framework (DRF), SimpleJWT.
- **AI Microservice**: FastAPI, Google Gemini 1.5 Pro, LangChain (RAG/Prompt Engineering).
- **Frontend**: React 19, React Router 7, Axios, Framer Motion (Animations).
- **Visualization**: Chart.js (Radar, Doughnut, Polar charts).
- **Storage/Data**: PostgreSQL (Primary), Redis (Caching), Local Filesystem (Documents).

---

## Architecture

The platform follows a distributed microservices pattern:
- **Backend Service (Django)**: Owns the source of truth, user sessions, and business rules.
- **AI Service (FastAPI)**: A stateless service that handles compute-heavy LLM tasks, specialized text extraction, and recommendation logic.
- **Frontend SPA (React)**: A highly interactive UI that aggregates data from both services to provide a seamless user experience.

---

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 16
- A Google Gemini API Key

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mohamed-bouchoucha/smart-pfe-platform.git
   cd smart-pfe-platform
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

3. **AI Service Setup**:
   ```bash
   cd ../ai-service
   pip install -r requirements.txt
   # Ensure GEMINI_API_KEY is set in .env
   uvicorn main:app --port 8001 --reload
   ```

4. **Frontend Setup**:
   ```bash
   cd ../frontend
   npm install
   npm start
   ```

---

## Project Structure

```text
smart-pfe-platform/
├── backend/            # Core REST API (Django)
│   ├── accounts/       # User management & RBAC logic
│   ├── projects/       # Project, Application, and Review models
│   └── recommendations/# Signal-based notification system
├── ai-service/         # AI Microservice (FastAPI)
│   ├── routers/        # Skill matching & ARIA chatbot logic
│   └── main.py         # Service entry point
├── frontend/           # Modern SPA (React 19)
│   ├── src/components/ # Reusable UI & Visualization components
│   └── src/pages/      # Dashboard, Kanban, and Chat interfaces
└── docs/               # Technical specifications & UML diagrams
```

---

## 📚 Technical Resources

| Resource | Description |
|----------|-------------|
| [Architecture Guide](docs/architecture.md) | High-level distributed architecture diagram. |
| [UML Class Diagram](docs/uml_class_diagram.md) | Full domain model and object relationships. |
| [Database Schema](docs/database_diagram.md) | Entity-Relationship diagram for PostgreSQL. |
| [API Specification](docs/api_specification.md) | OpenAPI/REST endpoint definitions. |

---

## Roadmap

- [ ] **Real-time Collaboration**: WebSocket integration for instant messaging between students and supervisors.
- [ ] **Advanced RAG**: Indexing uploaded PDF documents into a vector database (ChromaDB) for better AI context.
- [ ] **Mobile App**: Flutter or React Native client for on-the-go tracking.
- [ ] **Dockerization**: Full multi-container deployment using Docker Compose.

---

## Contributing

We welcome contributions. Please follow these steps:
1. Fork the project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## Notes
- This project uses **Google Gemini 1.5 Pro** for AI reasoning.
- Ensure all sensitive data (API keys, DB credentials) are stored in `.env` files and never committed to version control.
