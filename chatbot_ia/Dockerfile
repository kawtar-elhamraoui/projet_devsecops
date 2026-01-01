# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 1. Installer les dépendances système minimales
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 2. Configurer pip pour éviter les timeout
RUN pip config set global.timeout 1000 && \
    pip config set global.default-timeout 1000

# 3. Copier requirements
COPY requirements.txt .

# 4. Installer les dépendances avec retry
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
    --retries 10 \
    --timeout 600 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt

# 5. Installer manuellement les packages problématiques
RUN pip install --no-cache-dir onnx==1.14.0 --timeout 600 || \
    pip install --no-cache-dir onnxruntime==1.15.1 --timeout 600

# 6. Copier le code de l'application
COPY . .

# 7. Créer les dossiers nécessaires
RUN mkdir -p /app/chroma_db /app/knowledge_base/docs

# 8. Exposer le port
EXPOSE 8501

# 9. Exécuter l'application
CMD ["streamlit", "run", "chatbot_rag.py", "--server.port=8501", "--server.address=0.0.0.0"]