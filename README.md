# 🚀 Projet DevSecOps - Intégration Sécurité + Chatbot IA

## 📌 Aperçu
Projet de démonstration d'intégration de la sécurité dans un pipeline CI/CD avec un chatbot IA pour la détection automatisée des bugs.

## 🏗️ Architecture
- **Micro-API** : FastAPI avec endpoints sécurisés/vulnérables
- **Pipeline CI/CD** : GitHub Actions avec scans SAST/SCA
- **Chatbot IA** : Streamlit + RAG pour questions sécurité

## 🚀 Installation Rapide

### 1. Cloner et installer
```bash
git clone <votre-repo>
cd projet_devsecops

# Micro-API
cd micro_app
pip install -r requirements.txt

# Chatbot
cd ../chatbot_ia
pip install -r requirements.txt