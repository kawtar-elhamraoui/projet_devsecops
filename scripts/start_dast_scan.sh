#!/bin/bash
echo "🔍 Démarrage du scan DAST..."

# Démarrer l'API
docker-compose -f docker-compose.test.yml up -d
sleep 10

# Lancer ZAP
docker run -v $(pwd)/security-scans/dast:/zap/wrk \
  -t owasp/zap2docker-stable zap-baseline.py \
  -t http://host.docker.internal:8000 \
  -r zap-report.html \
  -c .zap/rules.tsv

# Lancer Nuclei
docker run -v $(pwd)/configs/nuclei-templates:/templates \
  -v $(pwd)/security-scans/dast:/reports \
  projectdiscovery/nuclei \
  -u http://localhost:8000 \
  -t /templates/custom-api-tests.yaml \
  -o /reports/nuclei-report.json

echo "✅ Scan DAST terminé"