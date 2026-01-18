import gradio as gr
import json
import PyPDF2
import numpy as np
from sentence_transformers import SentenceTransformer
import requests
import os
import time

# ===================================
# Variables globales
# ===================================
text_chunks = []
embeddings = []
embedding_model = None
OLLAMA_MODEL = "llama3.2:3b"  # Modèle plus léger (nécessite ~2GB au lieu de 4.6GB)

# ===================================
# Embeddings
# ===================================
def init_embedding_model():
    global embedding_model
    if embedding_model is None:
        print("🔄 Chargement embeddings...")
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Embeddings chargés")
    return embedding_model

# ===================================
# Extraction texte
# ===================================
def extract_text_from_pdf(path):
    text = ""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

def extract_text_from_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_text_from_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.dumps(json.load(f), indent=2, ensure_ascii=False)

# ===================================
# Split et similarité
# ===================================
def split_text(text, size=500, overlap=100):
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i+size])
        i += size - overlap
    return chunks

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def find_similar_chunks(query, top_k=3):
    """Retourne les top_k chunks les plus similaires"""
    q_emb = embedding_model.encode([query])[0]
    scores = [(i, cosine_similarity(q_emb, emb)) for i, emb in enumerate(embeddings)]
    scores.sort(key=lambda x: x[1], reverse=True)
    
    # Retourner les top_k meilleurs chunks
    top_chunks = [text_chunks[idx] for idx, score in scores[:top_k]]
    return "\n\n".join(top_chunks)

# ===================================
# Ollama - Optimisé pour modèles légers
# ===================================

def call_ollama_chat(prompt):
    try:
        print(f"📡 Appel à Ollama ({OLLAMA_MODEL})...")
        
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 400  # Réduit pour économiser la mémoire
                }
            },
            timeout=120
        )
        
        print(f"📊 Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            
            if "message" in data and "content" in data["message"]:
                response = data["message"]["content"]
                print(f"✅ Réponse reçue ({len(response)} chars)")
                return response
            else:
                return f"❌ Format inattendu: {data}"
        elif r.status_code == 500:
            error_data = r.json()
            if "more system memory" in str(error_data):
                return "❌ Mémoire insuffisante. Change de modèle dans le code (utilise tinyllama ou llama3.2:3b)"
            return f"❌ Erreur serveur: {error_data}"
        else:
            return f"❌ Erreur HTTP {r.status_code}: {r.text}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Impossible de se connecter à Ollama. Lance `ollama serve`"
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

def call_ollama_generate_stream(prompt):
    try:
        print(f"📡 Génération streaming ({OLLAMA_MODEL})...")
        
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 400
                }
            },
            stream=True,
            timeout=120
        )
        
        full_response = ""
        for line in r.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    
                    # Vérifier les erreurs
                    if "error" in data:
                        print(f"❌ Erreur Ollama: {data['error']}")
                        if "more system memory" in data['error']:
                            return "❌ Mémoire insuffisante. Utilise un modèle plus léger (tinyllama)"
                        return f"❌ {data['error']}"
                    
                    if "response" in data:
                        full_response += data["response"]
                    
                    if data.get("done", False):
                        print(f"✅ Génération terminée")
                        break
                except json.JSONDecodeError:
                    continue
        
        return full_response if full_response else "❌ Réponse vide"
            
    except requests.exceptions.ConnectionError:
        return "❌ Impossible de se connecter à Ollama. Lance `ollama serve`"
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

def call_ollama(prompt):
    # Essayer Chat API d'abord
    result = call_ollama_chat(prompt)
    if result and not result.startswith("❌"):
        return result
    
    # Sinon essayer Generate streaming
    print("⚠️ Chat API a échoué, essai streaming...")
    result = call_ollama_generate_stream(prompt)
    return result

# ===================================
# Traitement fichier
# ===================================
def process_file(file):
    global text_chunks, embeddings
    
    if file is None:
        return "❌ Aucun fichier sélectionné"
    
    init_embedding_model()
    path = file.name
    
    try:
        if path.endswith(".pdf"):
            text = extract_text_from_pdf(path)
        elif path.endswith(".txt"):
            text = extract_text_from_txt(path)
        elif path.endswith(".json"):
            text = extract_text_from_json(path)
        else:
            return "❌ Format non supporté (PDF, TXT, JSON uniquement)"

        if not text.strip():
            return "❌ Le fichier est vide"

        text_chunks = split_text(text)
        embeddings = embedding_model.encode(text_chunks)
        
        return f"✅ Fichier chargé avec succès!\n📄 {len(text_chunks)} chunks générés\n📊 Prêt pour les questions"
    
    except Exception as e:
        return f"❌ Erreur lors du traitement: {str(e)}"

# ===================================
# Questions
# ===================================
def ask_question(message, chat_history):
    if chat_history is None:
        chat_history = []

    if not message or not message.strip():
        return chat_history

    if not text_chunks:
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": "⚠️ Charge d'abord un document avant de poser des questions"})
        return chat_history

    # Trouver les chunks pertinents
    context = find_similar_chunks(message, top_k=2)  # Réduit à 2 pour économiser tokens
    
    # Créer le prompt optimisé
    prompt = f"""Réponds brièvement à la question en utilisant ce contexte :

{context}

Question: {message}
Réponse courte et claire:"""

    print(f"\n📝 Question: {message}")

    # Appeler Ollama
    answer = call_ollama(prompt)

    print(f"💬 Réponse: {answer[:100]}...\n")

    # Ajouter à l'historique
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": answer})

    return chat_history

# ===================================
# Interface
# ===================================
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Chatbot RAG – DevSecOps")
    gr.Markdown(f"**Modèle utilisé:** {OLLAMA_MODEL}")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📁 Charger un document")
            file_input = gr.File(label="Sélectionne un fichier", file_types=[".pdf", ".txt", ".json"])
            upload_btn = gr.Button("📤 Charger le fichier", variant="primary")
            status_output = gr.Textbox(label="📊 Statut", lines=6, interactive=False)
            
            gr.Markdown("### ℹ️ Instructions")
            gr.Markdown("""
            1. Upload un fichier PDF, TXT ou JSON
            2. Clique sur "Charger le fichier"
            3. Pose tes questions dans le chat
            """)
            
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Conversation")
            chatbot = gr.Chatbot(label="Chat", height=450)
            msg = gr.Textbox(
                label="Pose ta question ici",
                placeholder="Ex: Quels sont les points clés ?",
                lines=2
            )
            with gr.Row():
                send_btn = gr.Button("📨 Envoyer", variant="primary")
                clear_btn = gr.Button("🗑️ Effacer")

    # Événements
    upload_btn.click(process_file, inputs=file_input, outputs=status_output)
    
    send_btn.click(ask_question, inputs=[msg, chatbot], outputs=chatbot).then(
        lambda: "", None, msg
    )
    
    msg.submit(ask_question, inputs=[msg, chatbot], outputs=chatbot).then(
        lambda: "", None, msg
    )
    
    clear_btn.click(lambda: [], None, chatbot)

# ===================================
# Lancer app
# ===================================
if __name__ == "__main__":
    print("🚀 Lancement du chatbot RAG DevSecOps")
    print("="*60)
    print(f"🤖 Modèle: {OLLAMA_MODEL}")
    print("📡 Vérifie qu'Ollama est lancé: ollama serve")
    
    # Test de connexion
    try:
        test_response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if test_response.status_code == 200:
            models = test_response.json().get("models", [])
            print(f"✅ Ollama connecté - {len(models)} modèles disponibles")
            
            # Vérifier si le modèle choisi existe
            model_names = [m.get('name', '') for m in models]
            if OLLAMA_MODEL not in model_names:
                print(f"⚠️ ATTENTION: {OLLAMA_MODEL} n'est pas installé!")
                print(f"   Installe-le avec: ollama pull {OLLAMA_MODEL}")
            else:
                print(f"✅ {OLLAMA_MODEL} est disponible")
    except:
        print("❌ Ollama n'est pas accessible")
    
    print("="*60)
    demo.launch(share=False, server_name="127.0.0.1", server_port=7860)