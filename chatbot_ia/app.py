import streamlit as st
import json

st.set_page_config(page_title="Chatbot DevSecOps", page_icon="🤖")

st.title("🤖 Assistant DevSecOps IA")
st.markdown("### Posez vos questions sur la sécurité DevOps")

# Base de connaissances DEVSEOPS
knowledge = {
    "devsecops": {
        "definition": "DevSecOps = Développement + Sécurité + Opérations",
        "description": "Intègre la sécurité dans TOUT le cycle de développement, pas à la fin.",
        "avantages": "• Détection précoce des vulnérabilités\n• Réduction des coûts\n• Livraison plus rapide et sécurisée"
    },
    "sast": {
        "definition": "SAST = Static Application Security Testing",
        "description": "Analyse le code source SANS l'exécuter. Trouve des vulnérabilités statiques.",
        "outils": "• SonarQube\n• Bandit (Python)\n• Semgrep"
    },
    "dast": {
        "definition": "DAST = Dynamic Application Security Testing",
        "description": "Teste l'application EN FONCTIONNEMENT. Simule des attaques réelles.",
        "outils": "• OWASP ZAP\n• Burp Suite"
    },
    "sca": {
        "definition": "SCA = Software Composition Analysis",
        "description": "Analyse les dépendances/bibliothèques tierces pour vulnérabilités connues.",
        "outils": "• OWASP Dependency-Check\n• Snyk\n• Trivy"
    },
    "trivy": {
        "definition": "Scanner de vulnérabilités pour conteneurs Docker",
        "usage": "Scan les images Docker pour CVE connues",
        "commande": "`trivy image nom-image:tag`"
    },
    "pipeline": {
        "etapes": "1. Commit code → 2. Build → 3. Tests unitaires → 4. SAST → 5. SCA → 6. Build Docker → 7. Scan Docker → 8. Déploiement",
        "outil": "GitHub Actions / Jenkins"
    },
    "api": {
        "notre_projet": "API FastAPI avec endpoints GET/POST",
        "url": "http://localhost:8000",
        "endpoints": "• GET / → Accueil\n• GET /items → Liste items\n• POST /items → Créer item"
    },
    "chatbot": {
        "fonction": "Assistant IA pour questions DevSecOps",
        "techno": "Streamlit + Python"
    }
}

# Interface principale
st.sidebar.header("📋 Menu Rapide")

# Sélection par dropdown
option = st.sidebar.selectbox(
    "Choisir un sujet:",
    ["DevSecOps", "SAST", "DAST", "SCA", "Trivy", "Pipeline", "API", "Chatbot"]
)

if option:
    key = option.lower()
    if key in knowledge:
        info = knowledge[key]
        st.subheader(f"📚 {option.upper()}")
        
        for title, content in info.items():
            st.markdown(f"**{title.title()}:**")
            st.info(content)
            st.write("")

# Zone de questions personnalisées
st.markdown("---")
st.subheader("💬 Posez votre question")

question = st.text_input("Tapez votre question:")

if question:
    question_lower = question.lower()
    found = False
    
    for key, info in knowledge.items():
        if key in question_lower:
            st.success(f"**Sujet trouvé: {key.upper()}**")
            st.json(info)
            found = True
            break
    
    if not found:
        st.warning("""
        **Réponse générale:**
        
        Notre projet DevSecOps démontre l'intégration de la sécurité dans un pipeline CI/CD.
        
        **Composants:**
        1. **API FastAPI** - Application démo avec endpoints
        2. **Pipeline GitHub Actions** - Automatisation des tests de sécurité
        3. **Chatbot IA** - Cet assistant pour questions sécurité
        
        **Outils utilisés:** Python, FastAPI, Streamlit, Bandit, Trivy
        """)

# Simulation de rapports
st.sidebar.header("📊 Simulation Rapports")
if st.sidebar.button("📋 Rapport SAST (Bandit)"):
    st.subheader("📋 Rapport SAST - Bandit")
    st.json({
        "timestamp": "2024-12-31 18:00:00",
        "fichiers_analysés": 3,
        "vulnérabilités": {
            "critiques": 0,
            "hautes": 1,
            "moyennes": 2,
            "basses": 1
        },
        "recommandations": [
            "Utiliser des requêtes paramétrées pour éviter les injections SQL",
            "Valider les entrées utilisateur",
            "Mettre à jour les dépendances"
        ],
        "status": "✅ Pipeline réussi - Aucune vulnérabilité critique"
    })

if st.sidebar.button("🐳 Rapport Docker Scan (Trivy)"):
    st.subheader("🐳 Scan Docker - Trivy")
    st.json({
        "image": "micro-app:latest",
        "vulnérabilités": {
            "CRITICAL": 0,
            "HIGH": 1,
            "MEDIUM": 3,
            "LOW": 5
        },
        "recommandations": [
            "Mettre à jour l'image de base Python",
            "Supprimer les packages inutilisés",
            "Utiliser une image Alpine plus légère"
        ]
    })

# Footer
st.markdown("---")
st.markdown("""
**🔒 Projet DevSecOps - Sécurité Intégrée**
- **API:** http://localhost:8000
- **Code source:** https://github.com/votre-user/projet_devsecops
- **Pipeline:** GitHub Actions avec scans automatisés
""")