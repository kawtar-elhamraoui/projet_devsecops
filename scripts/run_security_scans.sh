#!/bin/bash
# run_security_scans.sh

echo "🔒 Lancement des scans de sécurité DevSecOps..."

# Créer le dossier de rapports
mkdir -p security-reports

# 1. Démarrer l'API
echo "1. Démarrage de l'API..."
cd micro_app
docker-compose up -d
sleep 10

# 2. SAST avec Bandit
echo "2. SAST - Bandit..."
bandit -r src/ -f json -o ../security-reports/bandit-report.json

# 3. SCA avec Safety
echo "3. SCA - Safety..."
safety check -r requirements.txt --json > ../security-reports/safety-report.json

# 4. Docker scan avec Trivy
echo "4. Container Scan - Trivy..."
docker build -t micro-app:scan .
trivy image micro-app:scan --format json -o ../security-reports/trivy-report.json

# 5. DAST avec ZAP
echo "5. DAST - OWASP ZAP..."
cd ..
chmod +x dast-scan.sh
./dast-scan.sh

# 6. Rapport consolidé
echo "6. Génération du rapport consolidé..."
python3 << 'EOF'
import json
from datetime import datetime

# Lire les rapports
reports = {
    "date": datetime.now().isoformat(),
    "sast": {},
    "sca": {},
    "dast": {},
    "container": {}
}

try:
    with open("security-reports/bandit-report.json") as f:
        sast_data = json.load(f)
        reports["sast"]["issues"] = len(sast_data.get("results", []))
        reports["sast"]["severity"] = {
            "high": sum(1 for r in sast_data.get("results", []) if r.get("issue_severity") == "HIGH"),
            "medium": sum(1 for r in sast_data.get("results", []) if r.get("issue_severity") == "MEDIUM"),
            "low": sum(1 for r in sast_data.get("results", []) if r.get("issue_severity") == "LOW")
        }
except:
    reports["sast"]["error"] = "Rapport non disponible"

# Générer le résumé
summary = f"""# 📊 Rapport de Sécurité Consolidé

## Projet DevSecOps
Date: {reports['date']}

## Résumé par Outil
### SAST (Bandit)
- Total issues: {reports['sast'].get('issues', 0)}
- High: {reports['sast'].get('severity', {}).get('high', 0)}
- Medium: {reports['sast'].get('severity', {}).get('medium', 0)}
- Low: {reports['sast'].get('severity', {}).get('low', 0)}

### DAST (OWASP ZAP)
- Scan dynamique terminé
- Consultez zap-report.html pour les détails

## Recommandations
1. Corriger les vulnérabilités HIGH prioritaires
2. Mettre à jour les dépendances vulnérables
3. Réviser les résultats du scan DAST
4. Implémenter les correctifs dans la prochaine itération

## Fichiers disponibles
- sast/bandit-report.json
- sca/safety-report.json
- container/trivy-report.json
- dast/zap-report.html
- dast/zap-report.json
"""

with open("security-reports/security-summary.md", "w") as f:
    f.write(summary)

print("Rapport généré avec succès")
EOF

# 7. Arrêter l'API
echo "7. Nettoyage..."
cd micro_app
docker-compose down

echo "✅ Tous les scans sont terminés !"
echo "📁 Consultez les rapports dans: security-reports/"