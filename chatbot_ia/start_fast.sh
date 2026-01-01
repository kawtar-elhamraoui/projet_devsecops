@echo off
echo ========================================
echo   CHATBOT RAG - VERSION LÉGÈRE
echo ========================================
echo.

REM 1. Créer la structure
echo [1/5] Création des dossiers...
if not exist "knowledge_base\docs" mkdir knowledge_base\docs
if not exist "chroma_db" mkdir chroma_db

REM 2. Créer requirements.txt léger
echo [2/5] Création requirements.txt...
(
echo streamlit==1.28.1
echo langchain==0.0.340
echo langchain-community==0.0.20
echo pypdf==3.17.0
echo chromadb==0.4.10
echo python-dotenv==1.0.0
echo numpy==1.24.3
echo ollama==0.1.4
echo fastembed==0.3.0
echo pydantic==1.10.13
echo typing-extensions==4.7.1
echo aiohttp==3.8.5
) > requirements.txt

REM 3. Supprimer les conteneurs existants
echo [3/5] Nettoyage...
docker-compose down -v 2>nul
docker system prune -f 2>nul

REM 4. Construire sans cache
echo [4/5] Construction Docker...
docker-compose build --no-cache --progress=plain

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERREUR BUILD - Tentative alternative...
    echo Construction étape par étape...
    
    REM Construction manuelle
    docker build -t chatbot-rag -f Dockerfile --progress=plain .
    
    if %errorlevel% neq 0 (
        echo.
        echo ❌ ERREUR CRITIQUE
        echo Solutions possibles:
        echo 1. Vérifiez votre connexion Internet
        echo 2. Essayez avec un VPN
        echo 3. Utilisez un miroir pip
        echo.
        pause
        exit /b 1
    )
)

REM 5. Démarrer
echo [5/5] Démarrage...
docker-compose up -d

REM 6. Vérification
timeout /t 30 /nobreak >nul

echo.
echo ========================================
echo            ✅ CHATBOT PRÊT !
echo ========================================
echo.
echo 🌐 Chatbot: http://localhost:8501
echo 🔧 Ollama: http://localhost:11434
echo.
echo 📋 Commandes utiles:
echo   docker-compose logs -f chatbot
echo   docker-compose restart chatbot
echo   docker exec ollama-tinyllama ollama pull tinyllama
echo.
echo ⚠️ Si le chatbot ne répond pas:
echo   1. Attendez 1-2 minutes
echo   2. docker-compose restart chatbot
echo   3. Vérifiez les logs: docker-compose logs chatbot
echo.
pause