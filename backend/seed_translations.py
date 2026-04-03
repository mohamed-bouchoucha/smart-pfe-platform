import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from projects.models import Project

def seed_translations():
    projects = Project.objects.all()
    translations = {
        "Système de recommandation PFE": ("PFE Recommendation System", "AI-based system to match students with the best projects."),
        "Chatbot IA pour l'orientation": ("AI Orientation Chatbot", "Intelligent chatbot helping students choose their career path."),
        "Plateforme Smart PFE": ("Smart PFE Platform", "A comprehensive platform for managing end-of-study projects."),
        "Analyse de sentiments Twitter": ("Twitter Sentiment Analysis", "Extracting insights from social media using NLP."),
    }

    count = 0
    for p in projects:
        if p.title in translations:
            en_title, en_desc = translations[p.title]
            p.title_en = en_title
            p.description_en = en_desc
            p.save()
            count += 1
            print(f"Updated: {p.title} -> {en_title}")
    
    print(f"Finished updating {count} projects.")

if __name__ == "__main__":
    seed_translations()
