import streamlit as st
from pathlib import Path
import re
import os

# =======================
# CONFIG STREAMLIT
# =======================
st.set_page_config(
    page_title="Chatbot RAG DevSecOps",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Assistant DevSecOps Intelligent")
st.markdown("💬 Je réponds à vos questions en analysant vos documents uploadés")

# =======================
# IMPORTS
# =======================
try:
    from langchain.document_loaders import TextLoader, PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    st.sidebar.success("✅ Système opérationnel")
except ImportError as e:
    st.error(f"❌ Dépendance manquante : {e}")
    st.stop()

# =======================
# SIDEBAR
# =======================
with st.sidebar:
    st.header("⚙️ Configuration")
    uploaded_file = st.file_uploader("📤 Ajouter un document", type=["txt", "pdf"])

    if uploaded_file:
        docs_path = Path("./knowledge_base/docs")
        docs_path.mkdir(parents=True, exist_ok=True)

        file_path = docs_path / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ {uploaded_file.name} ajouté avec succès")
        st.cache_resource.clear()
        st.rerun()

# =======================
# UTILS
# =======================
def clean_text(text: str) -> str:
    """Nettoie et normalise le texte"""
    if not text:
        return ""
    text = " ".join(text.split())
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    return text.strip()

def load_documents(docs_path: Path):
    """Charge tous les documents disponibles"""
    documents = []
    
    if not docs_path.exists():
        return documents

    for file in docs_path.iterdir():
        if not file.is_file():
            continue
            
        try:
            if file.suffix.lower() == ".txt":
                loader = TextLoader(str(file), encoding="utf-8")
                docs = loader.load()
                for d in docs:
                    d.metadata = {"source": file.name, "type": "txt"}
                documents.extend(docs)

            elif file.suffix.lower() == ".pdf":
                try:
                    loader = PyPDFLoader(str(file))
                    docs = loader.load()
                    for d in docs:
                        d.page_content = clean_text(d.page_content)
                        d.metadata = {
                            "source": file.name,
                            "type": "pdf",
                            "page": d.metadata.get("page", 0)
                        }
                    documents.extend(docs)
                except Exception as e:
                    st.sidebar.warning(f"⚠️ Erreur PDF {file.name}")
                    
        except Exception as e:
            st.sidebar.warning(f"⚠️ Erreur lecture {file.name}")

    return documents

# =======================
# MOTEUR DE RECHERCHE INTELLIGENT
# =======================
class SmartSearchEngine:
    def __init__(self, documents):
        self.documents = documents
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.chunks = self._create_chunks()
    
    def _create_chunks(self):
        """Découpe les documents en chunks pertinents"""
        all_chunks = []
        for doc in self.documents:
            chunks = self.splitter.split_text(doc.page_content)
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    "content": chunk,
                    "metadata": doc.metadata,
                    "chunk_id": i
                })
        return all_chunks
    
    def search(self, query: str, top_k: int = 5):
        """Recherche les chunks les plus pertinents"""
        query_lower = query.lower()
        query_words = [w for w in re.findall(r'\b\w+\b', query_lower) if len(w) >= 3]
        
        scored_chunks = []
        for chunk in self.chunks:
            content_lower = chunk["content"].lower()
            score = 0
            
            # Score basé sur les mots-clés
            for word in query_words:
                count = content_lower.count(word)
                score += count * (1 + len(word) * 0.1)
            
            # Bonus pour correspondance exacte
            if query_lower in content_lower:
                score += 10
            
            # Bonus pour les phrases complètes
            if len(chunk["content"]) > 100:
                score += 1
            
            if score > 0:
                scored_chunks.append((score, chunk))
        
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        return [chunk for score, chunk in scored_chunks[:top_k]]

# =======================
# GÉNÉRATEUR DE RÉPONSES INTELLIGENTES
# =======================
class ResponseGenerator:
    def __init__(self):
        self.response_templates = {
            "definition": [
                "D'après les documents, {}",
                "Selon l'information disponible, {}",
                "Voici ce que j'ai trouvé : {}"
            ],
            "howto": [
                "Pour {}, voici les étapes : \n\n{}",
                "La procédure pour {} est la suivante : \n\n{}"
            ],
            "list": [
                "Voici les éléments principaux concernant {} : \n\n{}",
                "J'ai identifié les points suivants sur {} : \n\n{}"
            ]
        }
    
    def generate(self, question: str, search_results: list) -> str:
        """Génère une réponse naturelle et cohérente"""
        if not search_results:
            return self._no_result_response(question)
        
        # Analyse du type de question
        question_type = self._detect_question_type(question)
        
        # Extraction des informations pertinentes
        relevant_info = self._extract_relevant_info(search_results, question)
        
        # Construction de la réponse
        response = self._build_response(question, question_type, relevant_info, search_results)
        
        return response
    
    def _detect_question_type(self, question: str) -> str:
        """Détecte le type de question posée"""
        q_lower = question.lower()
        
        if any(word in q_lower for word in ["c'est quoi", "qu'est-ce que", "définition", "définir"]):
            return "definition"
        elif any(word in q_lower for word in ["comment", "procédure", "étapes", "faire"]):
            return "howto"
        elif any(word in q_lower for word in ["liste", "quels sont", "différents", "types"]):
            return "list"
        else:
            return "general"
    
    def _extract_relevant_info(self, search_results: list, question: str) -> dict:
        """Extrait les informations les plus pertinentes"""
        q_words = set(re.findall(r'\b\w{4,}\b', question.lower()))
        
        sentences = []
        key_points = []
        examples = []
        
        for result in search_results[:3]:  # Top 3 résultats
            content = result["content"]
            
            # Découpe en phrases
            for sentence in re.split(r'[.!?]\s+', content):
                sentence = sentence.strip()
                if len(sentence) < 20:
                    continue
                
                s_lower = sentence.lower()
                relevance = sum(1 for word in q_words if word in s_lower)
                
                if relevance > 0:
                    sentences.append((relevance, sentence))
                
                # Détection d'exemples
                if any(marker in s_lower for marker in ["exemple", "example", "par exemple"]):
                    examples.append(sentence)
                
                # Détection de points clés
                if any(marker in s_lower for marker in ["important", "essentiel", "clé", "permet"]):
                    key_points.append(sentence)
        
        sentences.sort(reverse=True, key=lambda x: x[0])
        
        return {
            "sentences": [s for _, s in sentences[:5]],
            "key_points": key_points[:3],
            "examples": examples[:2],
            "sources": list(set([r["metadata"]["source"] for r in search_results]))
        }
    
    def _build_response(self, question: str, q_type: str, info: dict, results: list) -> str:
        """Construit une réponse naturelle et structurée"""
        response_parts = []
        
        # Introduction contextuelle
        if info["sentences"]:
            main_info = ". ".join(info["sentences"][:2])
            response_parts.append(f"{main_info}.")
            response_parts.append("")
        
        # Points clés si disponibles
        if info["key_points"]:
            response_parts.append("**Points importants :**")
            for i, point in enumerate(info["key_points"], 1):
                response_parts.append(f"- {point}")
            response_parts.append("")
        
        # Exemples si disponibles
        if info["examples"]:
            response_parts.append("**Exemple concret :**")
            response_parts.append(info["examples"][0])
            response_parts.append("")
        
        # Informations supplémentaires
        if len(info["sentences"]) > 2:
            response_parts.append("**Détails supplémentaires :**")
            for sentence in info["sentences"][2:4]:
                response_parts.append(f"• {sentence}")
            response_parts.append("")
        
        # Code ou commandes si c'est du DevSecOps
        code_snippet = self._extract_code(results)
        if code_snippet:
            response_parts.append("**Commandes ou configuration :**")
            response_parts.append(f"```bash\n{code_snippet}\n```")
            response_parts.append("")
        
        # Sources
        if info["sources"]:
            response_parts.append("---")
            response_parts.append(f"📚 *Sources : {', '.join(info['sources'])}*")
        
        return "\n".join(response_parts)
    
    def _extract_code(self, results: list) -> str:
        """Extrait des snippets de code des résultats"""
        for result in results:
            content = result["content"]
            # Recherche de commandes shell
            commands = re.findall(r'(?:^|\n)\s*[\$#]\s*(.+)', content, re.MULTILINE)
            if commands:
                return "\n".join([f"$ {cmd.strip()}" for cmd in commands[:5]])
            
            # Recherche de blocs de code
            code_blocks = re.findall(r'```[\s\S]*?```', content)
            if code_blocks:
                return code_blocks[0].replace('```', '').strip()
        
        return ""
    
    def _no_result_response(self, question: str) -> str:
        """Réponse quand aucune information n'est trouvée"""
        return f"""🤔 Je n'ai pas trouvé d'information pertinente dans les documents uploadés pour répondre à : 

*"{question}"*

**Suggestions :**
- Vérifiez que vos documents contiennent des informations sur ce sujet
- Reformulez votre question avec d'autres termes
- Ajoutez des documents supplémentaires via le panneau latéral

💡 *Astuce : Plus vos documents sont détaillés, meilleures seront mes réponses !*"""

# =======================
# INITIALISATION
# =======================
@st.cache_resource
def init_system():
    """Initialise le système RAG"""
    docs_path = Path("./knowledge_base/docs")
    
    if not docs_path.exists():
        st.sidebar.warning("📭 Aucun document chargé")
        return None, None

    documents = load_documents(docs_path)
    if not documents:
        st.sidebar.warning("📭 Aucun document valide trouvé")
        return None, None
    
    # Statistiques
    txt_count = sum(1 for d in documents if d.metadata.get("type") == "txt")
    pdf_count = sum(1 for d in documents if d.metadata.get("type") == "pdf")
    st.sidebar.success(f"✅ {len(documents)} documents chargés")
    st.sidebar.info(f"📄 {txt_count} TXT | 📕 {pdf_count} PDF")

    # Liste des fichiers
    with st.sidebar.expander("📚 Documents disponibles"):
        files = sorted(set([d.metadata.get("source") for d in documents]))
        for f in files:
            st.write(f"• {f}")
    
    search_engine = SmartSearchEngine(documents)
    response_generator = ResponseGenerator()
    
    return search_engine, response_generator

# =======================
# INTERFACE CHAT
# =======================
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "👋 **Bonjour ! Je suis votre assistant DevSecOps.**\n\n"
            "Je peux vous aider en analysant les documents que vous uploadez. "
            "Posez-moi des questions sur :\n\n"
            "• Concepts de sécurité (SAST, DAST, SCA...)\n"
            "• Outils DevSecOps (Bandit, SonarQube, OWASP...)\n"
            "• Procédures et bonnes pratiques\n"
            "• Configuration CI/CD sécurisée\n\n"
            "📤 Commencez par uploader vos documents dans la barre latérale !"
        )
    }]

# Affichage de l'historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input utilisateur
if question := st.chat_input("💬 Posez votre question..."):
    # Affichage question
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Génération réponse
    with st.chat_message("assistant"):
        with st.spinner("🔍 Analyse de vos documents..."):
            search_engine, response_gen = init_system()
            
            if not search_engine or not response_gen:
                response = "❌ **Aucun document disponible.**\n\nVeuillez uploader des documents pour que je puisse vous aider."
            else:
                # Recherche
                results = search_engine.search(question, top_k=8)
                
                # Génération réponse
                response = response_gen.generate(question, results)

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("🤖 **Assistant RAG DevSecOps**")
st.sidebar.caption("Propulsé par LangChain & Streamlit")