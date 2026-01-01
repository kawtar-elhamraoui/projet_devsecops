import streamlit as st
import os
from pathlib import Path

# Configuration
st.set_page_config(
    page_title="Chatbot RAG DevSecOps",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Chatbot RAG DevSecOps")
st.markdown("Assistant IA basé sur vos documents")

# Vérifier les imports
try:
    from langchain.document_loaders import TextLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.vectorstores import Chroma
    from langchain.chains import RetrievalQA
    from langchain.llms import Ollama
    
    # Utiliser FastEmbed au lieu de sentence-transformers
    from langchain_community.embeddings import FastEmbedEmbeddings
    
    st.sidebar.success("✅ Dépendances chargées")
except ImportError as e:
    st.error(f"❌ Dépendance manquante: {e}")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Mode
    mode = st.radio("Mode:", ["RAG", "FAQ Simple"])
    
    # Gestion documents
    uploaded_file = st.file_uploader("Ajouter document", type=['txt'])
    
    if uploaded_file:
        docs_path = Path("./knowledge_base/docs")
        docs_path.mkdir(exist_ok=True)
        
        file_path = docs_path / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"✅ {uploaded_file.name} ajouté")
        st.cache_resource.clear()

# Initialiser RAG avec FastEmbed
@st.cache_resource
def init_rag():
    """Initialise le système RAG avec FastEmbed"""
    
    # Charger documents
    docs_path = Path("./knowledge_base/docs")
    if not docs_path.exists():
        docs_path.mkdir(parents=True)
        return None
    
    # Créer documents par défaut si vide
    txt_files = list(docs_path.glob("*.txt"))
    if not txt_files:
        st.sidebar.info("Création documents par défaut...")
        default_docs = {
            "devsecops.txt": """DevSecOps: Intégration de la sécurité dans DevOps.

Principes:
1. Shift Left: Sécurité dès le début du développement
2. Automatisation: Tests sécurité automatisés dans CI/CD
3. Collaboration: Sécurité responsabilité de toute l'équipe
4. Continuité: Sécurité continue, pas des audits ponctuels

Outils essentiels:
- SAST: Bandit (Python), SonarQube
- SCA: Safety, OWASP Dependency-Check
- Container: Trivy, Grype
- DAST: OWASP ZAP, Burp Suite

Pipeline typique:
Code → SAST → SCA → Build → Scan container → DAST → Deploy → Monitor""",
            
            "sast.txt": """SAST (Static Application Security Testing) - Analyse statique

Bandit pour Python:
Installation: pip install bandit

Commandes:
- Analyse simple: bandit -r src/
- Format JSON: bandit -r src/ -f json -o bandit-report.json
- Ignorer règles: bandit -r src/ --skip B101,B102

GitHub Actions intégration:
- name: SAST with Bandit
  run: |
    pip install bandit
    bandit -r src/ -f json -o bandit-report.json
    
- name: Upload report
  uses: actions/upload-artifact@v3
  with:
    name: sast-reports
    path: bandit-report.json

Règles détectées:
- SQL injection (B608)
- Command injection (B602)
- Hardcoded passwords (B105)
- Insecure deserialization (B403)""",
            
            "trivy.txt": """Trivy - Scanner de vulnérabilités Docker

Installation:
# Linux/Mac
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh

# Windows (via scoop)
scoop install trivy

Commandes:
- Scanner image: trivy image nginx:latest
- Filtre sévérité: trivy image --severity HIGH,CRITICAL mon-app
- Format JSON: trivy image --format json mon-app > report.json
- Ignorer non-fixed: trivy image --ignore-unfixed mon-app

GitHub Actions:
- name: Scan with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'mon-app:${{ github.sha }}'
    format: 'sarif'
    output: 'trivy-results.sarif'

Best practices Docker:
1. Utiliser images officielles (python:3.11-slim)
2. Exécuter en USER non-root
3. Mettre à jour régulièrement
4. Scanner dans le registre""",
            
            "pipeline.txt": """Pipeline DevSecOps Complet

Étapes:
1. PRÉ-COMMIT:
   - Git hooks sécurité
   - Pré-commit avec bandit, black

2. CI (Intégration Continue):
   - Build application
   - Tests unitaires
   - SAST: Bandit, SonarQube
   - SCA: Safety, Dependency-Check

3. BUILD CONTAINER:
   - Build Docker image
   - Scan: Trivy, Grype
   - Signer image: Cosign

4. DÉPLOIEMENT:
   - Tests intégration
   - DAST: OWASP ZAP
   - Validation configuration

5. PRODUCTION:
   - Monitoring sécurité
   - Runtime protection
   - Audit logs

Métriques:
- MTTD: Mean Time To Detect
- MTTR: Mean Time To Remediate
- Nombre vulnérabilités critiques
- Taux faux positifs"""
        }
        
        for name, content in default_docs.items():
            (docs_path / name).write_text(content)
        
        txt_files = list(docs_path.glob("*.txt"))
    
    # Charger tous les fichiers texte
    documents = []
    for file_path in txt_files:
        try:
            loader = TextLoader(str(file_path))
            loaded = loader.load()
            for doc in loaded:
                doc.metadata = {"source": file_path.name}
            documents.extend(loaded)
        except Exception as e:
            st.sidebar.warning(f"Erreur chargement {file_path}: {e}")
            continue
    
    if not documents:
        st.sidebar.warning("⚠️ Aucun document chargé")
        return None
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    chunks = text_splitter.split_documents(documents)
    
    # Créer embeddings avec FastEmbed
    try:
        embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    except:
        # Fallback
        from langchain.embeddings import FakeEmbeddings
        embeddings = FakeEmbeddings(size=384)
        st.sidebar.warning("⚠️ FastEmbed non disponible - mode test")
    
    # Créer vector store
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    
    st.sidebar.success(f"✅ Base RAG: {len(chunks)} chunks")
    return vectordb

# Initialiser Ollama - VERSION CORRIGÉE
@st.cache_resource
def init_llm():
    """Initialise TinyLLaMA via Ollama"""
    try:
        # Paramètres SIMPLIFIÉS qui fonctionnent
        llm = Ollama(
            model="tinyllama",
            temperature=0.1
            # Ne pas mettre num_predict ni timeout
        )
        st.sidebar.success("✅ Ollama connecté")
        return llm
    except Exception as e:
        st.sidebar.warning(f"⚠️ Ollama non disponible: {str(e)[:100]}")
        return None

# Interface chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 **Bonjour ! Je suis votre assistant DevSecOps.**\n\nJe peux répondre à vos questions sur:\n- 🔐 SAST/DAST/SCA\n- 🐳 Sécurité Docker\n- 🚀 Pipeline CI/CD\n- 🛠️ Outils (Bandit, Trivy, SonarQube)"}
    ]

# Afficher historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input utilisateur
if prompt := st.chat_input("Votre question sur DevSecOps..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Générer réponse
    with st.chat_message("assistant"):
        if mode == "RAG":
            with st.spinner("🔍 Recherche dans la base de connaissances..."):
                vectordb = init_rag()
                llm = init_llm()
                
                if vectordb:
                    try:
                        # Recherche similaire
                        docs = vectordb.similarity_search(prompt, k=3)
                        prompt_lower = prompt.lower()
                        
                        if docs:
                            # Construire le contexte
                            context = "\n\n".join([
                                f"{doc.page_content[:400]}..."
                                for doc in docs
                            ])
                            
                            # Générer réponse INTELLIGENTE
                            final_response = ""
                            
                            # 1. Essayer avec Ollama si disponible
                            if llm:
                                try:
                                    rag_prompt = f"""Réponds à cette question en utilisant ces informations:

INFORMATIONS:
{context}

QUESTION: {prompt}

RÉPONSE (sois concis et utile):"""
                                    
                                    response = llm(rag_prompt)
                                    final_response = f"**🤖 Réponse IA:**\n\n{response}\n\n---\n**📚 Sources utilisées:**"
                                except:
                                    # Si Ollama échoue, continuer avec le fallback
                                    pass
                            
                            # 2. Si pas de réponse Ollama, utiliser fallback intelligent
                            if not final_response:
                                # Détection de type de question
                                if "comment installer" in prompt_lower:
                                    words = prompt_lower.split()
                                    if "installer" in words:
                                        idx = words.index("installer")
                                        if idx + 1 < len(words):
                                            tool = words[idx + 1]
                                            if tool == "bandit":
                                                final_response = """**📦 Installation de Bandit:**

```bash
# Installation
pip install bandit

# Utilisation de base
bandit -r src/

# Pour CI/CD (format JSON)
bandit -r src/ -f json -o bandit-report.json

# Ignorer certaines règles
bandit -r src/ --skip B101,B102

# Niveau de sortie détaillé
bandit -r src/ -ll