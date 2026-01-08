#!/usr/bin/env python3
"""
Script DAST professionnel pour le projet DevSecOps
Génère un rapport HTML complet des vulnérabilités
"""
import requests
import json
import time
import os
from datetime import datetime
import webbrowser

class DASTScanner:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "scan_date": datetime.now().isoformat(),
            "target": base_url,
            "vulnerabilities": [],
            "statistics": {
                "total_tests": 0,
                "vulnerabilities_found": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
        
        # Créer le dossier pour les rapports
        os.makedirs("security-scans/dast", exist_ok=True)
    
    def check_api_status(self):
        """Vérifie si l'API est accessible"""
        print("🔌 Connexion à l'API...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ API accessible (Status: {response.status_code})")
                return True
            else:
                print(f"⚠️ API répond avec status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ ERREUR : L'API n'est pas accessible")
            print(f"   Vérifiez que l'API tourne sur {self.base_url}")
            print("   Commandes de vérification :")
            print("   - docker ps (pour voir les conteneurs)")
            print("   - curl http://localhost:8000/health")
            return False
        except Exception as e:
            print(f"❌ ERREUR : {e}")
            return False
    
    def test_sql_injection(self):
        """Tests de SQL Injection"""
        print("\n🔍 Test SQL Injection...")
        
        test_cases = [
            {
                "name": "Basic SQL Injection",
                "payload": "' OR '1'='1",
                "endpoint": "/search/{}",
                "method": "GET",
                "severity": "HIGH"
            },
            {
                "name": "Union-Based SQLi",
                "payload": "test' UNION SELECT NULL--",
                "endpoint": "/search/{}",
                "method": "GET",
                "severity": "HIGH"
            },
            {
                "name": "Comment-Based SQLi",
                "payload": "admin'--",
                "endpoint": "/search/{}",
                "method": "GET",
                "severity": "MEDIUM"
            }
        ]
        
        for test in test_cases:
            try:
                url = f"{self.base_url}{test['endpoint'].format(test['payload'])}"
                response = requests.get(url, timeout=5)
                
                # Vérifier les indicateurs de vulnérabilité
                is_vulnerable = any(indicator in response.text.lower() 
                                   for indicator in ['sql', 'vulnérable', 'injection', 'warning'])
                
                result = {
                    "test_name": test["name"],
                    "endpoint": test["endpoint"].format("{payload}"),
                    "payload": test["payload"],
                    "status": "VULNERABLE" if is_vulnerable else "SAFE",
                    "severity": test["severity"],
                    "response_code": response.status_code,
                    "notes": "Vulnérabilité intentionnelle pour démonstration SAST/DAST"
                }
                
                self.results["vulnerabilities"].append(result)
                
                if is_vulnerable:
                    self.results["statistics"]["vulnerabilities_found"] += 1
                    self.results["statistics"][test["severity"].lower()] += 1
                    print(f"  ⚠️  {test['name']}: VULNÉRABLE")
                else:
                    print(f"  ✅ {test['name']}: SÉCURISÉ")
                    
            except Exception as e:
                print(f"  ❌ {test['name']}: Erreur - {e}")
    
    def test_command_injection(self):
        """Tests de Command Injection"""
        print("\n🔍 Test Command Injection...")
        
        test_cases = [
            {
                "name": "Basic Command Execution",
                "payload": "echo DAST_TEST",
                "endpoint": "/run/{}",
                "method": "GET",
                "severity": "CRITICAL"
            },
            {
                "name": "System Command",
                "payload": "whoami",
                "endpoint": "/run/{}",
                "method": "GET",
                "severity": "CRITICAL"
            }
        ]
        
        for test in test_cases:
            try:
                url = f"{self.base_url}{test['endpoint'].format(test['payload'])}"
                response = requests.get(url, timeout=5)
                data = response.json()
                
                # Vérifier si la commande a été exécutée
                is_vulnerable = "output" in data and data["output"]
                
                result = {
                    "test_name": test["name"],
                    "endpoint": test["endpoint"].format("{payload}"),
                    "payload": test["payload"],
                    "status": "VULNERABLE" if is_vulnerable else "SAFE",
                    "severity": test["severity"],
                    "response_code": response.status_code,
                    "notes": "Commande exécutée avec succès - Vulnérabilité intentionnelle"
                }
                
                self.results["vulnerabilities"].append(result)
                
                if is_vulnerable:
                    self.results["statistics"]["vulnerabilities_found"] += 1
                    self.results["statistics"][test["severity"].lower()] += 1
                    print(f"  ⚠️  {test['name']}: VULNÉRABLE (commande exécutée)")
                else:
                    print(f"  ✅ {test['name']}: SÉCURISÉ")
                    
            except Exception as e:
                print(f"  ❌ {test['name']}: Erreur - {e}")
    
    def test_unsafe_deserialization(self):
        """Test de désérialisation dangereuse"""
        print("\n🔍 Test Unsafe Deserialization...")
        
        try:
            # Tester avec pickle (dangereux)
            test_data = "test"
            response = requests.post(
                f"{self.base_url}/load_data",
                data=test_data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            is_vulnerable = "pickle" in response.text.lower() or "deserialization" in response.text.lower()
            
            result = {
                "test_name": "Unsafe Pickle Deserialization",
                "endpoint": "/load_data",
                "payload": "Données test",
                "status": "VULNERABLE" if is_vulnerable else "SAFE",
                "severity": "CRITICAL",
                "response_code": response.status_code,
                "notes": "Pickle utilisé avec données utilisateur - Très dangereux"
            }
            
            self.results["vulnerabilities"].append(result)
            
            if is_vulnerable:
                self.results["statistics"]["vulnerabilities_found"] += 1
                self.results["statistics"]["critical"] += 1
                print("  ⚠️  Unsafe Deserialization: VULNÉRABLE")
            else:
                print("  ✅ Unsafe Deserialization: SÉCURISÉ")
                
        except Exception as e:
            print(f"  ❌ Unsafe Deserialization: Erreur - {e}")
    
    def generate_html_report(self):
        """Génère un rapport HTML professionnel"""
        print("\n📊 Génération du rapport HTML...")
        
        # Compter les vulnérabilités par sévérité
        severity_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }
        
        for vuln in self.results["vulnerabilities"]:
            if vuln["status"] == "VULNERABLE":
                severity_counts[vuln["severity"]] += 1
        
        # Générer le HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Rapport DAST - Projet DevSecOps</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f5f5f5;
                    padding: 20px;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    padding: 30px;
                }}
                
                header {{
                    text-align: center;
                    margin-bottom: 40px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #eaeaea;
                }}
                
                h1 {{
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                
                .subtitle {{
                    color: #7f8c8d;
                    font-size: 1.1em;
                }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                
                .stat-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                
                .stat-number {{
                    font-size: 2.5em;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                
                .critical {{ color: #e74c3c; }}
                .high {{ color: #e67e22; }}
                .medium {{ color: #f1c40f; }}
                .low {{ color: #3498db; }}
                .safe {{ color: #2ecc71; }}
                
                .vuln-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                
                .vuln-table th {{
                    background: #34495e;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                
                .vuln-table td {{
                    padding: 12px;
                    border-bottom: 1px solid #ddd;
                }}
                
                .vuln-table tr:nth-child(even) {{
                    background: #f8f9fa;
                }}
                
                .status-badge {{
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 0.8em;
                    font-weight: bold;
                }}
                
                .vulnerable {{ background: #ffebee; color: #c62828; }}
                .safe {{ background: #e8f5e9; color: #2e7d32; }}
                
                .severity-badge {{
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    color: white;
                }}
                
                .critical-badge {{ background: #c62828; }}
                .high-badge {{ background: #ef6c00; }}
                .medium-badge {{ background: #f9a825; }}
                .low-badge {{ background: #1565c0; }}
                
                footer {{
                    margin-top: 40px;
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 0.9em;
                    padding-top: 20px;
                    border-top: 1px solid #eaeaea;
                }}
                
                .info-box {{
                    background: #e3f2fd;
                    border-left: 4px solid #2196f3;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>🔍 Rapport DAST - Projet DevSecOps</h1>
                    <p class="subtitle">Scan dynamique de sécurité - {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                </header>
                
                <div class="info-box">
                    <strong>📌 Note importante :</strong> 
                    Ces vulnérabilités sont <strong>intentionnelles</strong> et font partie 
                    de la démonstration pédagogique du projet DevSecOps.
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{self.results['statistics']['vulnerabilities_found']}</div>
                        <div>Vulnérabilités trouvées</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number critical">{severity_counts['CRITICAL']}</div>
                        <div>Critiques</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number high">{severity_counts['HIGH']}</div>
                        <div>Élevées</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number medium">{severity_counts['MEDIUM']}</div>
                        <div>Moyennes</div>
                    </div>
                </div>
                
                <h2>📋 Informations du scan</h2>
                <table style="width: 100%; margin-bottom: 30px;">
                    <tr>
                        <td><strong>URL cible :</strong></td>
                        <td>{self.results['target']}</td>
                    </tr>
                    <tr>
                        <td><strong>Date du scan :</strong></td>
                        <td>{self.results['scan_date']}</td>
                    </tr>
                    <tr>
                        <td><strong>Total tests :</strong></td>
                        <td>{len(self.results['vulnerabilities'])}</td>
                    </tr>
                </table>
                
                <h2>⚠️ Vulnérabilités détectées</h2>
                <table class="vuln-table">
                    <thead>
                        <tr>
                            <th>Test</th>
                            <th>Endpoint</th>
                            <th>Sévérité</th>
                            <th>Statut</th>
                            <th>Notes</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for vuln in self.results["vulnerabilities"]:
            # Déterminer les classes CSS
            status_class = "vulnerable" if vuln["status"] == "VULNERABLE" else "safe"
            severity_class = vuln["severity"].lower() + "-badge"
            
            html += f"""
                        <tr>
                            <td><strong>{vuln['test_name']}</strong></td>
                            <td><code>{vuln['endpoint']}</code></td>
                            <td><span class="severity-badge {severity_class}">{vuln['severity']}</span></td>
                            <td><span class="status-badge {status_class}">{vuln['status']}</span></td>
                            <td>{vuln['notes']}</td>
                        </tr>
            """
        
        html += f"""
                    </tbody>
                </table>
                
                <h2>🎓 Contexte pédagogique</h2>
                <div class="info-box">
                    <p><strong>Objectif du projet :</strong> Démontrer l'intégration de la sécurité dans le DevOps</p>
                    <p><strong>Vulnérabilités intentionnelles :</strong> Oui, pour l'apprentissage et la démonstration SAST/DAST</p>
                    <p><strong>Comparaison :</strong> Endpoints vulnérables vs endpoints sécurisés (préfixe /secure/)</p>
                </div>
                
                <h2>🛡️ Recommandations de sécurité</h2>
                <ul style="margin-left: 20px; margin-bottom: 30px;">
                    <li>Utiliser des requêtes paramétrées pour éviter les injections SQL</li>
                    <li>Ne jamais utiliser pickle.loads() avec des données non fiables</li>
                    <li>Valider et échapper toutes les entrées utilisateur</li>
                    <li>Utiliser subprocess.run() avec shell=False</li>
                    <li>Implémenter un WAF (Web Application Firewall)</li>
                </ul>
                
                <h2>🔗 Liens utiles</h2>
                <ul style="margin-left: 20px;">
                    <li><a href="https://sonarcloud.io/project/overview?id=kwtar-elhai_projet_devsecops" target="_blank">SonarCloud (SAST)</a></li>
                    <li><a href="https://owasp.org/www-project-top-ten/" target="_blank">OWASP Top 10</a></li>
                    <li><a href="https://cheatsheetseries.owasp.org/" target="_blank">OWASP Cheat Sheets</a></li>
                </ul>
                
                <footer>
                    <p>Rapport généré automatiquement par le scanner DAST du projet DevSecOps</p>
                    <p>Projet académique - Intégration de la sécurité à l'approche DevOps</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        # Sauvegarder le rapport
        report_path = "security-scans/dast/dast-report.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Rapport généré : {report_path}")
        return report_path
    
    def generate_json_report(self):
        """Génère un rapport JSON pour analyse"""
        report_path = "security-scans/dast/dast-report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"✅ Rapport JSON généré : {report_path}")
    
    def run_full_scan(self):
        """Exécute le scan complet"""
        print("=" * 60)
        print("🔒 SCAN DAST - Projet DevSecOps")
        print("=" * 60)
        
        # Vérifier l'API
        if not self.check_api_status():
            return False
        
        # Exécuter les tests
        self.results["statistics"]["total_tests"] = 7  # Nombre total de tests
        
        self.test_sql_injection()
        time.sleep(1)  # Petite pause entre les tests
        
        self.test_command_injection()
        time.sleep(1)
        
        self.test_unsafe_deserialization()
        
        # Générer les rapports
        html_report = self.generate_html_report()
        self.generate_json_report()
        
        # Afficher le résumé
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DU SCAN")
        print("=" * 60)
        print(f"🔗 URL testée : {self.base_url}")
        print(f"📅 Date du scan : {self.results['scan_date']}")
        print(f"🔍 Tests exécutés : {self.results['statistics']['total_tests']}")
        print(f"⚠️ Vulnérabilités trouvées : {self.results['statistics']['vulnerabilities_found']}")
        print(f"   • Critiques : {self.results['statistics']['critical']}")
        print(f"   • Élevées : {self.results['statistics']['high']}")
        print(f"   • Moyennes : {self.results['statistics']['medium']}")
        print(f"   • Faibles : {self.results['statistics']['low']}")
        
        print("\n✅ SCAN TERMINÉ AVEC SUCCÈS")
        print(f"📁 Rapports disponibles dans : security-scans/dast/")
        print(f"🌐 Ouvrir le rapport : file:///{os.path.abspath(html_report)}")
        
        return True

def main():
    """Fonction principale"""
    scanner = DASTScanner()
    
    if scanner.run_full_scan():
        # Demander si ouvrir le rapport
        choice = input("\nVoulez-vous ouvrir le rapport HTML maintenant ? (o/n) : ")
        if choice.lower() == 'o':
            report_path = os.path.abspath("security-scans/dast/dast-report.html")
            webbrowser.open(f"file:///{report_path}")
            print(f"🌐 Rapport ouvert dans le navigateur")
    else:
        print("\n❌ Le scan a échoué. Vérifiez que l'API est en cours d'exécution.")
        print("   Commandes utiles :")
        print("   - docker ps (vérifier les conteneurs)")
        print("   - curl http://localhost:8000/health (tester l'API)")

if __name__ == "__main__":
    main()