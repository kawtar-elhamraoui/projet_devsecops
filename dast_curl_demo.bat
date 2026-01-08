@echo off
chcp 65001 >nul
echo ===========================================
echo   DÉMONSTRATION DAST - Projet DevSecOps
echo   (Présentation au Professeur)
echo ===========================================
echo.

echo 📊 ÉTAPE 1 : Vérification des conteneurs Docker...
docker ps
echo.

echo 📊 ÉTAPE 2 : Test de l'API principale...
curl -s http://localhost:8000/health
echo.

echo 🔍 ÉTAPE 3 : Démontration des vulnérabilités INTENTIONNELLES...
echo.
echo ========== SQL INJECTION ==========
curl -s "http://localhost:8000/search/test' OR '1'='1"
echo.
echo ✅ DÉMONTRÉ : Injection SQL possible
echo.

echo ========== COMMAND INJECTION ==========
curl -s "http://localhost:8000/run/echo%20HACKED"
echo.
echo ✅ DÉMONTRÉ : Exécution de commandes possible
echo.

echo ========== UNSAFE DESERIALIZATION ==========
echo Test avec une donnée simple...
curl -s -X POST "http://localhost:8000/load_data" -H "Content-Type: application/json" -d "test"
echo.
echo ✅ DÉMONTRÉ : Désérialisation dangereuse
echo.

echo 📄 ÉTAPE 4 : Génération du rapport pour le professeur...
(
echo # 🎓 RAPPORT DE DÉMONSTRATION - Projet DevSecOps
echo.
echo **Date** : %date% %time%
echo **Étudiant** : [Votre Nom]
echo **Projet** : Intégration de la Sécurité à l'Approche DevOps
echo.
echo ## 📋 OBJECTIFS DÉMONTRÉS
echo.
echo ### 1. ✅ Intégration DevSecOps
echo - Pipeline CI/CD avec GitHub Actions
echo - Tests de sécurité automatisés (SAST/SCA/DAST)
echo - Détection des vulnérabilités en continu
echo.
echo ### 2. ✅ Démonstration pédagogique
echo - **Vulnérabilités intentionnelles** pour l'apprentissage
echo - Comparaison code vulnérable vs code sécurisé
echo - Outils professionnels utilisés (SonarCloud, OWASP, Bandit)
echo.
echo ### 3. ✅ Architecture moderne
echo - Microservices avec FastAPI
echo - Conteneurisation Docker
echo - Chatbot IA avec RAG (Retrieval Augmented Generation)
echo.
echo ## 🔍 VULNÉRABILITÉS DÉMONTRÉES
echo.
echo | Type | Endpoint | Détection | Intentionnel |
echo |------|----------|-----------|--------------|
echo | **SQL Injection** | `GET /search/{query}` | SAST (SonarCloud) + DAST | ✅ OUI |
echo | **Command Injection** | `GET /run/{command}` | SAST (SonarCloud) + DAST | ✅ OUI |
echo | **Unsafe Deserialization** | `POST /load_data` | SAST (Bandit) | ✅ OUI |
echo.
echo ## 🛡️ COMPOSANTS DU PROJET
echo.
echo ### A. Pipeline CI/CD (GitHub Actions)
echo 1. **SAST** : SonarCloud, Bandit
echo 2. **SCA** : Safety (dépendances Python)
echo 3. **Container Scan** : Trivy
echo 4. **DAST** : Tests dynamiques (ce script)
echo.
echo ### B. Application
echo 1. **API FastAPI** : micro_app/ (port 8000)
echo 2. **Chatbot IA** : chatbot_ia/ (port 8501)
echo 3. **Base de données** : SQLite pour démo
echo.
echo ### C. Outils de Sécurité
echo - **SonarCloud** : https://sonarcloud.io/project/overview?id=kwtar-elhai_projet_devsecops
echo - **Bandit** : Analyse sécurité Python
echo - **Safety** : Vulnérabilités des dépendances
echo - **Trivy** : Scan d'images Docker
echo.
echo ## 🎯 POUR LE PROFESSEUR
echo.
echo ### Liens importants :
echo 1. **SonarCloud (SAST)** : https://sonarcloud.io/project/overview?id=kwtar-elhai_projet_devsecops
echo 2. **Code source** : https://github.com/[votre-repo]
echo 3. **Pipeline CI/CD** : https://github.com/[votre-repo]/actions
echo.
echo ### Démo en direct :
echo ```bash
echo # 1. Voir les conteneurs
echo docker ps
echo.
echo # 2. Tester l'API
echo curl http://localhost:8000/devsecops/info
echo.
echo # 3. Voir les vulnérabilités
echo curl "http://localhost:8000/search/test' OR '1'='1"
echo ```
echo.
echo ## 📞 CONTACT
echo **Étudiant** : [Votre Nom]
echo **Email** : [votre.email@domain.com]
echo **GitHub** : https://github.com/[votre-username]
) > "Rapport pour le Professeur.md"

echo ✅ RAPPORT GÉNÉRÉ : "Rapport pour le Professeur.md"
echo.
echo ===========================================
echo   INSTRUCTIONS POUR LA PRÉSENTATION
echo ===========================================
echo.
echo 1. OUVREZ le rapport : "Rapport pour le Professeur.md"
echo 2. MONTRER les conteneurs : docker ps
echo 3. TESTER l'API : curl http://localhost:8000/devsecops/info
echo 4. MONTRER SonarCloud : https://sonarcloud.io
echo 5. LANCER le chatbot : http://localhost:8501
echo.
echo 📌 ASTUCE : Copiez ce rapport sur une clé USB pour le projet !
echo.
pause