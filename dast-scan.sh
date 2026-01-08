#!/bin/bash
echo "🔍 Démarrage du scan DAST local avec OWASP ZAP..."

# Variables
API_URL="http://localhost:8000"
ZAP_PORT="8090"
REPORT_DIR="security-reports/dast"

# Créer le dossier de rapports
mkdir -p $REPORT_DIR

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Installez Docker d'abord."
    exit 1
fi

# Arrêter ZAP s'il est déjà en cours d'exécution
docker stop zap 2>/dev/null || true
docker rm zap 2>/dev/null || true

# Démarrer ZAP
echo "1. Démarrage de OWASP ZAP..."
docker run --rm -d \
  -p $ZAP_PORT:$ZAP_PORT \
  --name zap \
  owasp/zap2docker-stable zap.sh \
  -daemon -host 0.0.0.0 -port $ZAP_PORT \
  -config api.disablekey=true \
  -config api.addrs.addr.name=.* \
  -config api.addrs.addr.regex=true

echo "Attente du démarrage de ZAP..."
sleep 15

# Vérifier que l'API est accessible
echo "2. Vérification de l'API à $API_URL..."
if ! curl -s $API_URL > /dev/null; then
    echo "⚠️ L'API n'est pas accessible. Démarrez l'API d'abord:"
    echo "   cd micro_app && docker-compose up -d"
    docker stop zap
    exit 1
fi

# Scanner l'API (version simplifiée)
echo "3. Scanner l'API..."
docker exec zap zap-cli --zap-url http://localhost:$ZAP_PORT \
  quick-scan --self-contained \
  --start-options '-config api.disablekey=true' \
  $API_URL

# Générer les rapports
echo "4. Génération des rapports..."
docker exec zap zap-cli --zap-url http://localhost:$ZAP_PORT \
  report -o /zap/wrk/zap-report.html -f html

docker exec zap zap-cli --zap-url http://localhost:$ZAP_PORT \
  report -o /zap/wrk/zap-report.json -f json

# Copier les rapports
docker cp zap:/zap/wrk/zap-report.html $REPORT_DIR/
docker cp zap:/zap/wrk/zap-report.json $REPORT_DIR/

# Créer un résumé simple
echo "# Rapport DAST - OWASP ZAP" > $REPORT_DIR/zap-summary.md
echo "Date: $(date)" >> $REPORT_DIR/zap-summary.md
echo "API Scannée: $API_URL" >> $REPORT_DIR/zap-summary.md
echo "" >> $REPORT_DIR/zap-summary.md
echo "## Comment visualiser les résultats:" >> $REPORT_DIR/zap-summary.md
echo "1. Ouvrez le fichier: $REPORT_DIR/zap-report.html dans votre navigateur" >> $REPORT_DIR/zap-summary.md
echo "2. Consultez les vulnérabilités trouvées" >> $REPORT_DIR/zap-summary.md
echo "3. Les alertes sont classées par risque (High, Medium, Low)" >> $REPORT_DIR/zap-summary.md

# Nettoyage
echo "5. Nettoyage..."
docker stop zap

echo ""
echo "✅ Scan DAST terminé avec succès !"
echo "📊 Rapports disponibles dans: $REPORT_DIR/"
echo "🌐 Ouvrez ce fichier dans votre navigateur:"
echo "   file://$(pwd)/$REPORT_DIR/zap-report.html"