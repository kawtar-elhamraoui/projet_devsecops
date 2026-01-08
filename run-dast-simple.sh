#!/bin/bash
echo "🚀 Démarrage rapide du scan DAST..."

# Démarrer l'API si elle ne l'est pas déjà
cd micro_app
docker-compose up -d
cd ..

# Attendre que l'API soit prête
echo "⏳ Attente du démarrage de l'API..."
sleep 8

# Exécuter le scan DAST
chmod +x dast-scan.sh
./dast-scan.sh

# Ouvrir automatiquement le rapport (Mac)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open security-reports/dast/zap-report.html
# Ouvrir automatiquement le rapport (Linux)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open security-reports/dast/zap-report.html 2>/dev/null || echo "Rapport généré: security-reports/dast/zap-report.html"
fi