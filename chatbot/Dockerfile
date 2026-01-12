FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'application
COPY . .

# Créer les répertoires pour les fichiers
RUN mkdir -p /app/data /app/uploads

# Exposer le port
EXPOSE 7860

# Lancer l'application
CMD ["python", "app.py"]