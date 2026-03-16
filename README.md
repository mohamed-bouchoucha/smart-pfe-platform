# 🎓 Smart PFE Platform

> Plateforme intelligente pour la recherche de projets de PFE et stages en Génie Logiciel

[![Django](https://img.shields.io/badge/Django-6.0-green?logo=django)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-19-blue?logo=react)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-teal?logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://postgresql.org)

---

## 📋 Description

Smart PFE Platform est une application web full-stack qui aide les étudiants en informatique à :

- 🔍 **Trouver** des idées de projets de PFE pertinentes
- 🤖 **Interagir** avec un chatbot IA pour clarifier leurs besoins
- 📊 **Recevoir** des recommandations personnalisées basées sur leurs compétences
- 📁 **Uploader** des documents (CV, cahier des charges) pour une analyse IA

## 🏗️ Architecture

```
smart-pfe-platform/
├── frontend/          # React 19 (SPA)
├── backend/           # Django 6 + DRF (API REST)
├── ai-service/        # FastAPI (Microservice IA)
└── docs/              # Documentation technique
```

> Voir [docs/architecture.md](docs/architecture.md) pour le diagramme complet.

## ⚡ Démarrage Rapide

### Prérequis
- Python 3.12+
- Node.js 20+
- PostgreSQL 16

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### AI Service
```bash
cd ai-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

## 🔑 Variables d'Environnement

Créer un fichier `.env` :

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:pass@localhost:5432/smart_pfe

# AI Service
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | Diagramme d'architecture microservices |
| [UML Classes](docs/uml_class_diagram.md) | Diagramme de classes complet |
| [Base de Données](docs/database_diagram.md) | Schéma ER de la base de données |
| [API Spec](docs/api_specification.md) | Spécification des endpoints REST |

## 🛠️ Technologies

| Couche | Technologies |
|--------|-------------|
| **Frontend** | React 19, React Router 7, Axios, Framer Motion, Chart.js |
| **Backend** | Django 6, DRF, SimpleJWT, django-cors-headers |
| **IA** | FastAPI, Google Gemini, LangChain, ChromaDB |
| **Base de données** | PostgreSQL 16, Redis |
| **Infrastructure** | Docker, Nginx, Celery |

## 👥 Rôles

- **Admin** : Gestion des utilisateurs, validation des projets, statistiques
- **Étudiant** : Chatbot IA, recherche de projets, upload de documents, favoris

## 📄 Licence

Projet de fin d'études — Usage académique uniquement.
