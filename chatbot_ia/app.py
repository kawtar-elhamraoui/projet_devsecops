import streamlit as st
import json
import requests

st.set_page_config(page_title="Chatbot DevSecOps", page_icon="🤖")

st.title("🤖 Assistant DevSecOps IA")
st.markdown("### Posez vos questions sur la sécurité DevOps")

# Base de connaissances améliorée avec RÉPONSES DIRECTES
knowledge = {
    "devsecops": "**DevSecOps** = Développement + Sécurité + Opérations. Intègre la sécurité dans TOUT le cycle de développement, pas seulement à la fin.",
    "sast": "**SAST** (Static Application Security Testing) analyse le code source SANS l'exécuter. Outils: SonarQube, Bandit, Semgrep.",
    "dast": "**DAST** (Dynamic Application Security Testing) teste l'application EN FONCTIONNEMENT. Outils: OWASP ZAP, Burp Suite.",
    "sca": "**SCA** (Software Composition Analysis) analyse les dépendances tierces. Outils: OWASP Dependency-Check, Snyk.",
    "trivy": "**Trivy** scanne les images Docker pour vulnérabilités. Commande: `trivy image nom-image:tag`",
    "sonarqube": "**SonarQube** est un outil SAST qui analyse la qualité du code. Il trouve bugs, vulnérabilités et code smells.",
    "pipeline": "Un pipeline DevSecOps typique: 1. Code → 2. Tests → 3. SAST → 4. SCA → 5. Build Docker → 6. Scan → 7. Déploiement",
    "vulnérabilité": "Une vulnérabilité est une faille de sécurité. Types courants: injection SQL, XSS, command injection.",
    "injection": "L'injection SQL est une attaque où du code SQL malveillant est injecté. Prévention: requêtes paramétrées.",
    "docker": "Docker permet la conteneurisation. Sécurité: scanner les images avec Trivy avant déploiement.",
    "github actions": "GitHub Actions est notre pipeline CI/CD. Il exécute automatiquement les tests de sécurité.",
    "api": "Notre API FastAPI est accessible sur http://localhost:8000. Elle a des endpoints vulnérables et sécurisés.",
    "chatbot": "Je suis un chatbot IA pour questions DevSecOps. Je suis codé avec Streamlit et Python.",
    "projet": "Notre projet montre l'intégration sécurité dans DevOps. Composants: API, pipeline, chatbot.",
    "test": "Les tests automatisés sont essentiels. Notre pipeline exécute pytest, Bandit, Trivy automatiquement.",
    "sécurité": "La sécurité doit être 'shift left', intégrée dès le début du développement, pas à la fin.",
    "ci/cd": "CI = Intégration Continue, CD = Déploiement Continu. Notre pipeline CI/CD est sur GitHub Actions.",
    "outil": "Outils utilisés: SonarQube (SAST), Trivy (scan Docker), Bandit (SAST Python), OWASP ZAP (DAST).",
    "bandit": "Bandit est un outil SAST pour Python. Il trouve des vulnérabilités dans le code Python.",
    "zap": "OWASP ZAP est un outil DAST pour tester les applications web en fonctionnement.",
    "correction": "Pour corriger une vulnérabilité: 1. Identifier 2. Comprendre 3. Corriger 4. Tester 5. Valider.",
    "analyse": "Notre pipeline analyse automatiquement le code à chaque commit avec SonarQube.",
    "rapport": "Les rapports de sécurité sont générés automatiquement et accessibles sur SonarCloud.",
    "qualité": "La qualité du code est mesurée par: sécurité, fiabilité, maintenabilité, couverture tests.",
}

# Interface principale
st.sidebar.header("📋 Menu Rapide")

# Questions prédéfinies
if st.sidebar.button("❓ Qu'est-ce que DevSecOps?"):
    st.session_state.question = "devsecops"
if st.sidebar.button("🔍 C'est quoi SAST?"):
    st.session_state.question = "sast"
if st.sidebar.button("🐳 Comment scanner Docker?"):
    st.session_state.question = "trivy"
if st.sidebar.button("🚀 Notre pipeline?"):
    st.session_state.question = "pipeline"

# Zone de question
st.markdown("---")
st.subheader("💬 Posez votre question")

# Initialiser la question si dans session_state
default_question = st.session_state.get('question', '')
question = st.text_input("Tapez votre question:", value=default_question)

# Réinitialiser après utilisation
if 'question' in st.session_state:
    del st.session_state.question

if question and question.strip():
    question_lower = question.lower().strip()
    
    # Recherche intelligente
    response = None
    matched_keyword = None
    
    # Chercher par mot-clé
    for keyword, answer in knowledge.items():
        if keyword in question_lower:
            response = answer
            matched_keyword = keyword
            break
    
    # Si pas trouvé, chercher des mots similaires
    if not response:
        words = question_lower.split()
        for word in words:
            if word in knowledge:
                response = knowledge[word]
                matched_keyword = word
                break
    
    # Afficher réponse
    if response:
        st.success(f"**{matched_keyword.upper()}**" if matched_keyword else "**RÉPONSE**")
        st.info(response)
        
        # Suggestions
        st.markdown("**💡 Questions connexes:**")
        cols = st.columns(3)
        related = list(knowledge.keys())
        # Filtrer les mots-clés pertinents
        filtered = [k for k in related if k != matched_keyword and len(k) > 3][:6]
        for i, keyword in enumerate(filtered):
            if st.button(keyword, key=f"btn_{i}"):
                st.session_state.question = keyword
                st.rerun()
    else:
        # Réponse par défaut avec suggestions
        st.warning("""
        **Je suis votre assistant DevSecOps !** 
        
        Je peux répondre aux questions sur :
        
        **🎯 Concepts:** devsecops, sast, dast, sca, ci/cd  
        **🛠️ Outils:** sonarqube, trivy, bandit, docker, github actions  
        **🔐 Sécurité:** vulnérabilité, injection, test, analyse  
        **📊 Projet:** api, pipeline, rapport, qualité
        
        **Essayez:** "Comment fonctionne SonarQube?" ou "Quels outils DevSecOps utiliser?"
        """)
        
        # Afficher toutes les catégories
        with st.expander("📚 Voir toutes les catégories"):
            categories = {
                "Concepts": ["devsecops", "sast", "dast", "sca", "ci/cd", "pipeline"],
                "Outils": ["sonarqube", "trivy", "bandit", "docker", "github actions", "zap"],
                "Sécurité": ["vulnérabilité", "injection", "test", "sécurité", "correction"],
                "Projet": ["api", "projet", "chatbot", "analyse", "rapport"]
            }
            
            for category, items in categories.items():
                st.markdown(f"**{category}:**")
                cols = st.columns(3)
                for i, item in enumerate(items):
                    if item in knowledge:
                        if cols[i % 3].button(item, key=f"cat_{item}"):
                            st.session_state.question = item
                            st.rerun()

# Simulation de rapports
st.sidebar.header("📊 Simulation Rapports")
if st.sidebar.button("📋 Rapport SonarQube"):
    with st.spinner("Génération du rapport..."):
        st.subheader("📊 Rapport SonarQube - Dernière analyse")
        st.json({
            "date_analyse": "31/12/2025 21:09",
            "lignes_code": 344,
            "qualité": {
                "security": "E → A (après corrections)",
                "reliability": "A",
                "maintainability": "A"
            },
            "vulnérabilités": {
                "bloqueurs": 4,
                "critiques": 0,
                "majeures": 0,
                "mineures": 0
            },
            "types_détectés": [
                "SQL injection",
                "Command injection", 
                "Insecure deserialization"
            ],
            "lien": "https://sonarcloud.io/project/overview?id=kwtar-elhai_projet_devsecops"
        })

if st.sidebar.button("🧪 Tester l'API"):
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            st.sidebar.success("✅ API accessible")
            with st.sidebar.expander("Détails API"):
                st.json(response.json())
        else:
            st.sidebar.error(f"❌ API erreur: {response.status_code}")
    except Exception as e:
        st.sidebar.error("❌ API non accessible")
        st.sidebar.info("Lancez: `cd micro_app && docker-compose up -d`")

# Footer avec infos réelles
st.markdown("---")
st.markdown("""
**🔒 Projet DevSecOps - Sécurité Intégrée**

**🌐 API FastAPI:** http://localhost:8000  
**📊 SonarCloud:** https://sonarcloud.io/organizations/kawtar-elhamraoui/projects 
**🚀 GitHub Actions:** https://github.com/kawtar-elhamraoui/projet_devsecops/actions 
**🤖 Chatbot:** http://localhost:8501  

**🛠️ Stack technique:** FastAPI, Docker, GitHub Actions, SonarQube, Streamlit
""")

# Debug option
with st.sidebar.expander("🔧 Debug"):
    if st.button("Afficher base de connaissances"):
        st.write("Mots-clés disponibles:", list(knowledge.keys()))