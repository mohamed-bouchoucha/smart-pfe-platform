# Smart PFE Platform — Diagramme UML de Classes

## Diagramme de Classes Complet

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

## Description des Classes

| Classe | Responsabilité |
|--------|---------------|
| **User** | Gestion des utilisateurs (étudiants et admins) avec profil complet |
| **Project** | Projets de PFE/Stage avec domaine, technologies, et statut de validation |
| **Conversation** | Session de chat avec le chatbot IA |
| **Message** | Message individuel dans une conversation (user ou assistant) |
| **Document** | Fichiers uploadés (CV, cahier des charges, rapports) |
| **Favorite** | Liaison entre un utilisateur et ses projets favoris |
| **Recommendation** | Suggestion de projet générée par l'IA avec score de pertinence |
| **Skill** | Compétence technique (langage, framework, outil) |
| **Notification** | Alertes et notifications pour l'utilisateur |
| **AuditLog** | Journal d'audit pour tracer les actions des utilisateurs |
