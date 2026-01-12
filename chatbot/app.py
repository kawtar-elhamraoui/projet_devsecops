import gradio as gr
import json
import PyPDF2
import numpy as np
from sentence_transformers import SentenceTransformer
import requests
import os
import time

# Variables globales
text_chunks = []
embeddings = []
embedding_model = None

# ------------------------------
# Modèle d'embeddings
# ------------------------------
def init_embedding_model():
    global embedding_model
    if embedding_model is None:
        print("Chargement du modèle d'embeddings...")
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Modèle chargé !")
    return embedding_model

# ------------------------------
# Extraction de texte
# ------------------------------
def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text, None
    except Exception as e:
        return None, f"Erreur lors de la lecture du PDF: {str(e)}"

def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return text, None
    except Exception as e:
        return None, f"Erreur lors de la lecture du TXT: {str(e)}"

def extract_text_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        text = json.dumps(data, indent=2, ensure_ascii=False)
        return text, None
    except Exception as e:
        return None, f"Erreur lors de la lecture du JSON: {str(e)}"

# ------------------------------
# Découpage et similarité
# ------------------------------
def split_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def find_similar_chunks(query, top_k=1):
    global text_chunks, embeddings, embedding_model
    if not text_chunks:
        return []
    query_embedding = embedding_model.encode([query])[0]
    similarities = [(i, cosine_similarity(query_embedding, emb)) for i, emb in enumerate(embeddings)]
    similarities.sort(key=lambda x: x[1], reverse=True)
    return [text_chunks[i] for i, _ in similarities[:top_k]]

# ------------------------------
# Appel Ollama
# ------------------------------
def call_ollama(prompt):
    start_time = time.time()
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': 'llama3', 'prompt': prompt, 'stream': False},
            timeout=300  # 5 minutes
        )
        end_time = time.time()
        print(f"Temps Ollama: {end_time - start_time:.2f}s")
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"Erreur Ollama: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "❌ Ollama n'est pas lancé. Exécutez 'ollama serve'."
    except requests.exceptions.ReadTimeout:
        return "❌ Timeout : Ollama met trop de temps à répondre. Réduisez la taille du prompt ou vérifiez le modèle."
    except Exception as e:
        return f"❌ Erreur lors de l'appel à Ollama: {str(e)}"

# ------------------------------
# Traitement du fichier
# ------------------------------
def process_file(file):
    global text_chunks, embeddings, embedding_model
    if file is None:
        return "❌ Aucun fichier sélectionné."
    try:
        embedding_model = init_embedding_model()
        file_path = file.name if hasattr(file, 'name') else file
        file_name = os.path.basename(file_path).lower()
        if file_name.endswith('.pdf'):
            text, error = extract_text_from_pdf(file_path)
        elif file_name.endswith('.txt'):
            text, error = extract_text_from_txt(file_path)
        elif file_name.endswith('.json'):
            text, error = extract_text_from_json(file_path)
        else:
            return "❌ Format non supporté. Utilisez PDF, TXT ou JSON."
        if error:
            return error
        if not text or len(text.strip()) < 10:
            return "❌ Le fichier est vide ou ne contient pas assez de texte."
        text_chunks = split_text(text)
        print(f"Création des embeddings pour {len(text_chunks)} chunks...")
        embeddings = embedding_model.encode(text_chunks)
        print("Embeddings créés !")
        return f"✅ Fichier '{file_name}' chargé avec succès !\n\n📊 {len(text_chunks)} segments créés\n📝 {len(text)} caractères traités\n\n💬 Vous pouvez maintenant poser vos questions !"
    except Exception as e:
        return f"❌ Erreur lors du traitement: {str(e)}"

# ------------------------------
# Réponse aux questions
# ------------------------------
def ask_question(message, history):
    global text_chunks
    if not text_chunks:
        return "⚠️ Veuillez d'abord charger un fichier avant de poser des questions."
    if not message.strip():
        return "⚠️ Veuillez poser une question."
    try:
        similar_chunks = find_similar_chunks(message, top_k=1)  # plus rapide
        if not similar_chunks:
            return "Je n'ai pas trouvé d'informations pertinentes dans le fichier."
        context = "\n\n".join(similar_chunks)
        prompt = f"""Tu es un assistant intelligent. Réponds de manière claire, concise et pédagogique à la question ci-dessous en utilisant uniquement les informations suivantes :

Contexte :
{context}

Question :
{message}

Réponse :"""
        response = call_ollama(prompt)
        return response
    except Exception as e:
        return f"❌ Erreur: {str(e)}"

# ------------------------------
# Interface Gradio
# ------------------------------
with gr.Blocks(title="Chatbot RAG") as demo:
    gr.Markdown("# 📚 Chatbot RAG Intelligent ")
    gr.Markdown("Uploadez un fichier (PDF, TXT ou JSON) et posez vos questions !")
    
    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="📁 Importer votre fichier", file_types=[".pdf", ".txt", ".json"])
            upload_btn = gr.Button("⬆️ Charger le fichier", variant="primary", size="lg")
            status_output = gr.Textbox(label="📊 Statut", lines=6, interactive=False)
            reset_btn = gr.Button("🔄 Réinitialiser", variant="secondary")
        
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(height=500, label="💬 Conversation")
            msg = gr.Textbox(placeholder="Ex: Quels sont les points principaux du document ?", label="Posez votre question", lines=2)
            with gr.Row():
                submit = gr.Button("📤 Envoyer", variant="primary")
                clear = gr.Button("🗑️ Effacer")
    
    def respond(message, chat_history):
        if chat_history is None:
            chat_history = []
        bot_message = ask_question(message, chat_history)
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})
        return "", chat_history
    
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    submit.click(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)
    
    upload_btn.click(fn=process_file, inputs=[file_input], outputs=[status_output])
    reset_btn.click(fn=lambda: ([], ""), outputs=[chatbot, status_output])

if __name__ == "__main__":
    print("🚀 Démarrage du chatbot...")
    print("📦 Assurez-vous qu'Ollama est lancé avec 'ollama serve'")
    demo.launch(share=False, server_name="127.0.0.1", server_port=7860)
