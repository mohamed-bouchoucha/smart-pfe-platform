# Smart PFE Platform — Spécification API REST

## Base URL

```
http://localhost:8000/api/
```

## Authentification

Toutes les requêtes (sauf login/register) nécessitent un header :
```
Authorization: Bearer <access_token>
```

---

## 1. Auth Endpoints

### POST `/api/auth/register/`
Inscription d'un nouvel utilisateur.

**Body :**
```json
{
  "email": "[EMAIL_ADDRESS]",
  "username": "mohamed",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "Mohamed",
  "last_name": "Bouchoucha",
  "university": "Institut Superieur d'informatique et de mathematique de Monastir",
  "field_of_study": "Génie Logiciel"
}
```

**Response `201` :**
```json
{
  "id": 1,
  "email": "etudiant@univ.dz",
  "username": "mohamed",
  "tokens": {
    "access": "eyJ...",
    "refresh": "eyJ..."
  }
}
```

### POST `/api/auth/login/`
```json
{ "email": "etudiant@univ.dz", "password": "SecurePass123!" }
```

### POST `/api/auth/token/refresh/`
```json
{ "refresh": "eyJ..." }
```

---

## 2. Users Endpoints

### GET `/api/users/me/`
Profil de l'utilisateur connecté.

### PATCH `/api/users/me/`
Mettre à jour le profil.

### GET `/api/users/` *(Admin uniquement)*
Liste de tous les utilisateurs.

---

## 3. Projects Endpoints

### GET `/api/projects/`
Liste des projets validés avec filtres.

**Query Params :** `?domain=IA&difficulty=intermediate&search=deep+learning`

### POST `/api/projects/` *(Admin)*
Créer un nouveau projet.

### GET `/api/projects/{id}/`
Détails d'un projet.

### PATCH `/api/projects/{id}/validate/` *(Admin)*
Valider un projet.

---

## 4. Conversations Endpoints

### GET `/api/conversations/`
Historique des conversations du user.

### POST `/api/conversations/`
Créer une nouvelle conversation.

### GET `/api/conversations/{id}/messages/`
Messages d'une conversation.

### POST `/api/conversations/{id}/messages/`
Envoyer un message (déclenche le chatbot IA).

**Body :**
```json
{ "content": "Je cherche un PFE en intelligence artificielle" }
```

**Response `201` :**
```json
{
  "user_message": {
    "id": 1,
    "sender": "user",
    "content": "Je cherche un PFE en intelligence artificielle",
    "timestamp": "2026-03-16T17:30:00Z"
  },
  "assistant_message": {
    "id": 2,
    "sender": "assistant",
    "content": "Voici quelques idées de PFE en IA...",
    "metadata": {
      "suggestions": [
        { "project_id": 5, "title": "Système de recommandation NLP", "score": 0.92 }
      ]
    },
    "timestamp": "2026-03-16T17:30:02Z"
  }
}
```

---

## 5. Documents Endpoints

### POST `/api/documents/upload/`
Upload un fichier (multipart/form-data).

### GET `/api/documents/`
Liste des documents de l'utilisateur.

### DELETE `/api/documents/{id}/`
Supprimer un document.

---

## 6. Recommendations Endpoints

### GET `/api/recommendations/`
Recommandations personnalisées pour l'utilisateur.

---

## 7. Favorites Endpoints

### GET `/api/favorites/`
Projets favoris de l'utilisateur.

### POST `/api/favorites/`
```json
{ "project_id": 5 }
```

### DELETE `/api/favorites/{id}/`
Retirer un favori.

---

## 8. Admin Endpoints *(Admin uniquement)*

### GET `/api/admin/stats/`
Statistiques de la plateforme.

**Response :**
```json
{
  "total_users": 150,
  "total_projects": 45,
  "total_conversations": 320,
  "active_users_today": 28,
  "projects_by_domain": {
    "IA": 15, "Web": 12, "DevOps": 8, "DataScience": 6, "Cybersecurity": 4
  }
}
```

### GET `/api/admin/users/`
Liste complète des utilisateurs avec filtres.

### PATCH `/api/admin/projects/{id}/status/`
Changer le statut d'un projet (validate/reject).
