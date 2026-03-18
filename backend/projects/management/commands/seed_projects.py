from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import Project

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial PFE project ideas'

    def handle(self, *args, **kwargs):
        # 1. Get or create a user for assignment
        try:
            creator = User.objects.get(username='testuser101')
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING("User 'testuser101' not found. Using an admin user instead."))
            creator = User.objects.filter(is_superuser=True).first()
            if not creator:
                self.stdout.write(self.style.ERROR("No user found to assign projects. Run migrations/registration first."))
                return

        # 2. Define projects
        projects_data = [
            {
                "title": "Plateforme de Recrutement Intelligente",
                "description": "Développement d'une plateforme web pour l'analyse des CV et le matching candidats-postes en utilisant le NLP.",
                "domain": "IA",
                "technologies": "Python, React, Django, Scikit-learn",
                "difficulty": "intermediate",
                "duration": "4months",
                "company_name": "SmartTech Solutions"
            },
            {
                "title": "Application Mobile pour le Suivi de Santé",
                "description": "Conception et développement d'une application mobile multiplateforme pour le suivi des constantes vitales et rappels médicamenteux.",
                "domain": "Mobile",
                "technologies": "Flutter, Firebase, Node.js",
                "difficulty": "beginner",
                "duration": "3months",
                "company_name": "HealthCorp"
            },
            {
                "title": "Système de Monitoring IoT Agricole",
                "description": "Mise en place d'un réseau de capteurs pour surveiller l'humidité du sol et automatiser l'irrigation via une interface Cloud.",
                "domain": "IoT",
                "technologies": "Arduino, Raspberry Pi, Python, AWS IoT",
                "difficulty": "advanced",
                "duration": "6months",
                "company_name": "AgriGrow"
            },
            {
                "title": "Audit de Sécurité Automatisé",
                "description": "Création d'un dashboard de monitoring pour scanner les vulnérabilités courantes (OWASP) dans les applications web.",
                "domain": "Cybersecurity",
                "technologies": "Python, Docker, SQLMap, React",
                "difficulty": "advanced",
                "duration": "4months",
                "company_name": "SecuCloud"
            },
            {
                "title": "Visualisation de Données Logistiques",
                "description": "Dashboard interactif pour l'optimisation des flux de transport et la prévisibilité des retards de livraison.",
                "domain": "DataScience",
                "technologies": "D3.js, React, Pandas, FastAPI",
                "difficulty": "intermediate",
                "duration": "3months",
                "company_name": "LogiTrans"
            },
            {
                "title": "Application de Gestion de Projets Agiles",
                "description": "Outil collaboratif de gestion de tâches avec tableaux Kanban et rapports de performance automatique.",
                "domain": "Web",
                "technologies": "Next.js, Tailwind CSS, Prisma, PostgreSQL",
                "difficulty": "beginner",
                "duration": "2months",
                "company_name": "DevFactory"
            },
            {
                "title": "Analyse de Sentiments pour Réseaux Sociaux",
                "description": "Outil d'analyse en temps réel des commentaires sur les réseaux sociaux pour évaluer l'e-réputation d'une marque.",
                "domain": "IA",
                "technologies": "Python, HuggingFace, React, MongoDB",
                "difficulty": "advanced",
                "duration": "4months",
                "company_name": "BrandWatch"
            },
            {
                "title": "Porte-monnaie Crypto-monnaie Sécurisé",
                "description": "Implémentation d'une interface web sécurisée pour la gestion des transactions sur la blockchain Ethereum.",
                "domain": "Other",
                "technologies": "React, Ethers.js, Solidity",
                "difficulty": "advanced",
                "duration": "4months",
                "company_name": "CryptoSec"
            }
        ]

        # 3. Create projects
        count = 0
        for data in projects_data:
            project, created = Project.objects.get_or_create(
                title=data["title"],
                defaults={
                    "description": data["description"],
                    "domain": data["domain"],
                    "technologies": data["technologies"],
                    "difficulty": data["difficulty"],
                    "duration": data["duration"],
                    "status": "validated",
                    "company_name": data["company_name"],
                    "created_by": creator
                }
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {count} projects."))
