"""
Document Analysis Router — Analyzes uploaded documents and extracts project suggestions.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AnalyzeRequest(BaseModel):
    text: str
    doc_type: str = "cv"
    user_profile: dict = {}


class AnalyzeResponse(BaseModel):
    summary: str
    extracted_skills: list[str]
    suggested_domains: list[str]
    confidence: float


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_document(request: AnalyzeRequest):
    """Analyze a document and extract relevant information for project recommendations."""
    text_lower = request.text.lower()

    # Simple keyword-based skill extraction
    skill_keywords = {
        'python': 'Python', 'java': 'Java', 'javascript': 'JavaScript',
        'react': 'React', 'angular': 'Angular', 'vue': 'Vue.js',
        'django': 'Django', 'flask': 'Flask', 'fastapi': 'FastAPI',
        'node': 'Node.js', 'express': 'Express.js',
        'sql': 'SQL', 'postgresql': 'PostgreSQL', 'mysql': 'MySQL', 'mongodb': 'MongoDB',
        'docker': 'Docker', 'kubernetes': 'Kubernetes', 'aws': 'AWS', 'azure': 'Azure',
        'tensorflow': 'TensorFlow', 'pytorch': 'PyTorch', 'scikit': 'Scikit-learn',
        'machine learning': 'Machine Learning', 'deep learning': 'Deep Learning',
        'html': 'HTML', 'css': 'CSS', 'typescript': 'TypeScript',
        'git': 'Git', 'linux': 'Linux', 'ci/cd': 'CI/CD',
    }

    domain_keywords = {
        'IA': ['ia', 'intelligence artificielle', 'machine learning', 'deep learning', 'nlp', 'tensorflow', 'pytorch'],
        'Web': ['web', 'react', 'angular', 'vue', 'django', 'flask', 'html', 'css', 'frontend', 'backend'],
        'DevOps': ['devops', 'docker', 'kubernetes', 'ci/cd', 'aws', 'azure', 'cloud', 'terraform'],
        'DataScience': ['data', 'analyse', 'pandas', 'numpy', 'visualisation', 'statistique', 'big data'],
        'Cybersecurity': ['sécurité', 'cybersécurité', 'pentest', 'firewall', 'cryptographie', 'owasp'],
        'Mobile': ['mobile', 'android', 'ios', 'flutter', 'react native', 'kotlin', 'swift'],
    }

    # Extract skills
    extracted_skills = [
        display_name
        for keyword, display_name in skill_keywords.items()
        if keyword in text_lower
    ]

    # Suggest domains
    suggested_domains = []
    for domain, keywords in domain_keywords.items():
        if any(kw in text_lower for kw in keywords):
            suggested_domains.append(domain)

    if not suggested_domains:
        suggested_domains = ['Web']

    # Generate summary
    if request.doc_type == 'cv':
        summary = f"CV analysé : {len(extracted_skills)} compétences techniques détectées. "
        summary += f"Domaines suggérés : {', '.join(suggested_domains)}."
    else:
        summary = f"Document analysé ({request.doc_type}). "
        summary += f"Technologies identifiées : {', '.join(extracted_skills[:5]) if extracted_skills else 'Aucune détectée'}."

    return AnalyzeResponse(
        summary=summary,
        extracted_skills=extracted_skills,
        suggested_domains=suggested_domains,
        confidence=min(0.5 + len(extracted_skills) * 0.05, 0.95),
    )
