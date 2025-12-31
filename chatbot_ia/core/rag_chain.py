from langchain.chains import RetrievalQA
from langchain.llms import Ollama
import os

# Configuration simple - pour démo, utilise des réponses prédéfinies
def get_answer(question):
    answers = {
        "qu'est-ce que devsecops": "DevSecOps est l'intégration de la sécurité dans le pipeline DevOps. Sécurité continue!",
        "qu'est-ce que sast": "SAST = Static Application Security Testing. Analyse le code source.",
        "comment scanner une image docker": "Utilisez Trivy: trivy image nom-image",
        "quels outils utiliser": "GitHub Actions, Bandit, Trivy, SonarQube, OWASP ZAP",
        "bandit": "Bandit est un outil SAST pour Python qui trouve des vulnérabilités de sécurité.",
        "trivy": "Trivy scanne les images Docker pour les vulnérabilités connues.",
        "test": "Les tests sont essentiels dans DevSecOps. Automatisez-les!",
    }
    
    question_lower = question.lower()
    
    for key, answer in answers.items():
        if key in question_lower:
            return answer
    
    return "Je suis un chatbot DevSecOps en cours de développement. Pour l'instant, je peux répondre aux questions sur: DevSecOps, SAST, Bandit, Trivy, et les outils de sécurité."