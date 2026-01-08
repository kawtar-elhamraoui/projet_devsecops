@echo off
echo ========================================
echo     SCAN DAST RAPIDE - OWASP ZAP
echo ========================================
echo.

REM 1. Vérifier l'API
echo [1/4] Vérification de l'API...
curl http://localhost:8000/ >nul 2>&1
if errorlevel 1 (
    echo ❌ API non détectée. Démarrage en cours...
    cd micro_app
    docker-compose up -d
    timeout /t 5 /nobreak >nul
    cd ..
)

REM 2. Télécharger ZAP
echo [2/4] Téléchargement d'OWASP ZAP...
docker pull ghcr.io/zaproxy/zaproxy:stable

REM 3. Lancer le scan
echo [3/4] Lancement du scan de sécurité...
docker run --rm -v %cd%:/zap/wrk/:rw ^
  -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py ^
  -t http://host.docker.internal:8000 ^
  -r zap-report.html ^
  -a ^
  -x report.xml ^
  -j report.json

REM 4. Déplacer les rapports
echo [4/4] Organisation des rapports...
if not exist "security-reports\dast" mkdir "security-reports\dast"
move zap-report.html "security-reports\dast\" >nul 2>&1
move report.json "security-reports\dast\zap-report.json" >nul 2>&1
move report.xml "security-reports\dast\zap-report.xml" >nul 2>&1

echo.
echo ========================================
echo           ✅ SCAN TERMINÉ !
echo ========================================
echo.
echo 📊 Rapports générés :
echo - security-reports\dast\zap-report.html (HTML complet)
echo - security-reports\dast\zap-report.json (JSON)
echo - security-reports\dast\zap-report.xml (XML)
echo.
echo 🔍 Pour analyser plus en détail :
echo docker run --rm -p 8080:8080 ghcr.io/zaproxy/zaproxy:stable
echo.
echo Ouvrir le rapport...
start "" "security-reports\dast\zap-report.html"
pause