# Smart PFE Platform — Diagramme de Base de Données

## Modèle Entité-Relation (ER Diagram)

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

## Dictionnaire de Données

### Table USER
| Colonne | Type | Contrainte | Description |
|---------|------|-----------|-------------|
| id | INT | PK, AUTO_INCREMENT | Identifiant unique |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Adresse email |
| username | VARCHAR(150) | UNIQUE, NOT NULL | Nom d'utilisateur |
| password_hash | VARCHAR(255) | NOT NULL | Mot de passe hashé (bcrypt) |
| role | VARCHAR(20) | NOT NULL, DEFAULT 'student' | Rôle (admin/student) |
| university | VARCHAR(255) | NULL | Université |
| field_of_study | VARCHAR(255) | NULL | Domaine d'études |

### Table PROJECT
| Colonne | Type | Contrainte | Description |
|---------|------|-----------|-------------|
| id | INT | PK, AUTO_INCREMENT | Identifiant unique |
| title | VARCHAR(255) | NOT NULL | Titre du projet |
| domain | VARCHAR(100) | NOT NULL | Domaine (IA, Web, DevOps...) |
| difficulty | VARCHAR(20) | NOT NULL | Niveau de difficulté |
| status | VARCHAR(20) | DEFAULT 'draft' | Statut de validation |

### Indexes
- `IDX_user_email` on USER(email)
- `IDX_project_domain` on PROJECT(domain)
- `IDX_project_status` on PROJECT(status)
- `IDX_conversation_user` on CONVERSATION(user_id)
- `IDX_message_conversation` on MESSAGE(conversation_id)
- `IDX_favorite_user_project` on FAVORITE(user_id, project_id) UNIQUE
