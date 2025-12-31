#!/bin/bash

echo "🔒 Lancement des scans de sécurité..."

# SAST avec Bandit
echo "1. SAST - Bandit..."
cd micro_app
bandit -r src/ -f json -o ../security-reports/bandit-report.json

# SCA avec Safety
echo "2. SCA - Safety..."
safety check -r requirements.txt --json > ../security-reports/safety-report.json

# Docker scan avec Trivy
echo "3. Docker Scan - Trivy..."
docker build -t micro-app:scan .
trivy image micro-app:scan --format json -o ../security-reports/trivy-report.json

echo "✅ Scans terminés! Voir le dossier security-reports/"