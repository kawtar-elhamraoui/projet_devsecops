import sqlite3
import pickle
import subprocess
from fastapi import FastAPI, HTTPException
from datetime import datetime
import json
from typing import List, Optional
import uuid

# AJOUTER CET IMPORT MANQUANT !
from pydantic import BaseModel  # ← MANQUANT !

app = FastAPI(title="DevSecOps Demo API", version="1.0.0")

# ========== DÉFINITION DU MODÈLE ITEM ==========
class Item(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
# ==============================================

# Initialiser une base SQLite pour les tests
def init_db():
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price REAL
        )
    """)
    # Ajouter des données de test
    cursor.execute("INSERT OR IGNORE INTO products (name, price) VALUES ('Laptop', 999.99)")
    cursor.execute("INSERT OR IGNORE INTO products (name, price) VALUES ('Phone', 499.99)")
    cursor.execute("INSERT OR IGNORE INTO products (name, price) VALUES ('Tablet', 299.99)")
    conn.commit()
    conn.close()

# Initialiser la base au démarrage
init_db()

# ========== ENDPOINTS DE BASE ==========

@app.get("/")
def read_root():
    return {"message": "API DevSecOps - Projet de Fin d'Année", "status": "running"}

@app.get("/health")
def health_check():
    """Endpoint pour vérifier que l'API fonctionne"""
    return {
        "status": "healthy",
        "service": "DevSecOps API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/",
            "/health",
            "/search/{query}",
            "/load_data",
            "/run/{command}",
            "/test/vulnerable",
            "/items",
            "/secure/search/{query}",
            "/devsecops/info"
        ]
    }

# ========== ENDPOINTS VULNÉRABLES (POUR TESTS SAST) ==========

@app.get("/search/{query}")
def search(query: str):
    """⚠️ VULNÉRABLE : Injection SQL INTENTIONNELLE"""
    conn = sqlite3.connect("test.db")
    # VULNÉRABLE : concaténation directe - DANGER !
    cursor = conn.execute(f"SELECT * FROM products WHERE name = '{query}'")
    results = cursor.fetchall()
    conn.close()
    return {
        "query": f"SELECT * FROM products WHERE name = '{query}'",
        "results": results,
        "warning": "⚠️ CET ENDPOINT EST VULNÉRABLE À L'INJECTION SQL",
        "educational": "Pour démontrer la détection SAST avec SonarQube"
    }

@app.post("/load_data")
def load_data(data: str):
    """⚠️ VULNÉRABLE : Désérialisation pickle INTENTIONNELLE"""
    try:
        # VULNÉRABLE : pickle avec données utilisateur - TRÈS DANGEREUX !
        loaded = pickle.loads(data.encode())
        return {
            "data": str(loaded),
            "warning": "⚠️ NE JAMAIS utiliser pickle avec des données non fiables",
            "risk": "Arbitrary code execution possible",
            "secure_alternative": "Utiliser json.loads() à la place"
        }
    except Exception as e:
        return {"error": str(e), "type": "pickle deserialization"}

@app.get("/run/{command}")
def run_command(command: str):
    """⚠️ VULNÉRABLE : Command Injection INTENTIONNELLE"""
    # VULNÉRABLE : shell=True avec input utilisateur - DANGER !
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return {
        "output": result.stdout,
        "error": result.stderr,
        "returncode": result.returncode,
        "warning": "⚠️ COMMAND INJECTION RISK - shell=True avec input utilisateur",
        "secure_alternative": "Utiliser subprocess.run([cmd], shell=False)"
    }

@app.get("/test/vulnerable")
def test_vulnerable(param: str = "test"):
    """⚠️ VULNÉRABLE : Test multiple INTENTIONNEL"""
    # Multiples vulnérabilités pour démo
    vulnerabilities = []
    
    # 1. SQL Injection
    conn = sqlite3.connect("test.db")
    cursor = conn.execute(f"SELECT name FROM products WHERE name LIKE '%{param}%'")
    vulnerabilities.append(f"SQL: SELECT name FROM products WHERE name LIKE '%{param}%'")
    
    # 2. Command Injection
    subprocess.run(f"echo Testing: {param}", shell=True)
    vulnerabilities.append(f"Command: echo Testing: {param}")
    
    return {
        "param": param,
        "vulnerabilities": vulnerabilities,
        "message": "⚠️ MULTIPLES VULNÉRABILITÉS INTENTIONNELLES POUR DÉMONSTRATION SAST",
        "sonarqube_detection": "Ces patterns seront détectés par SonarQube comme: SQL injection, Command injection"
    }

# ========== ENDPOINTS SÉCURISÉS (BONNES PRATIQUES) ==========

@app.get("/secure/search/{query}")
def secure_search(query: str):
    """✅ VERSION SÉCURISÉE : Pas d'injection SQL"""
    # Validation input
    if not query.isalnum():
        raise HTTPException(status_code=400, detail="Query must be alphanumeric")
    
    conn = sqlite3.connect("test.db")
    # SÉCURISÉ : requête paramétrée
    cursor = conn.execute("SELECT * FROM products WHERE name = ?", (query,))
    results = cursor.fetchall()
    conn.close()
    
    return {
        "query": "SELECT * FROM products WHERE name = ?",
        "param": query,
        "results": results,
        "security": "✅ Requête paramétrée - Safe from SQL injection"
    }

@app.post("/secure/load")
def secure_load(data: str):
    """✅ VERSION SÉCURISÉE : JSON au lieu de pickle"""
    try:
        # SÉCURISÉ : JSON au lieu de pickle
        loaded = json.loads(data)
        return {
            "data": loaded,
            "method": "json.loads()",
            "security": "✅ JSON désérialisation - Safe from arbitrary code execution"
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

@app.get("/secure/run/{command}")
def secure_run(command: str):
    """✅ VERSION SÉCURISÉE : Pas de command injection"""
    # Validation commande
    allowed_commands = {"echo", "date", "pwd", "whoami"}
    if command not in allowed_commands:
        raise HTTPException(
            status_code=400,
            detail=f"Command not allowed. Allowed: {allowed_commands}"
        )
    
    # SÉCURISÉ : pas de shell=True, liste d'arguments
    result = subprocess.run([command], capture_output=True, text=True, shell=False)
    
    return {
        "output": result.stdout,
        "error": result.stderr,
        "security": "✅ Command execution sécurisée - shell=False, command validation"
    }

# ========== ENDPOINTS DE DÉMONSTRATION DEVSECOPS ==========

# Simule une base de données en mémoire
items_db = []

@app.get("/items", response_model=List[Item])
def get_items():
    """Endpoint de démo pour items"""
    return items_db

@app.post("/items", response_model=Item, status_code=201)
def create_item(name: str, description: Optional[str] = None):
    """Créer un item - avec validation"""
    if not name or len(name) > 100:
        raise HTTPException(status_code=400, detail="Invalid name")
    
    new_item = Item(
        id=str(uuid.uuid4()),
        name=name,
        description=description
    )
    items_db.append(new_item)
    return new_item

@app.get("/devsecops/info")
def devsecops_info():
    """Information sur l'implémentation DevSecOps"""
    return {
        "project": "Projet DevSecOps - PFE",
        "purpose": "Démonstration d'intégration sécurité dans DevOps",
        "components": {
            "api": "FastAPI avec endpoints vulnérables/sécurisés",
            "pipeline": "GitHub Actions CI/CD avec SAST/SCA/DAST",
            "tools": "SonarQube, Bandit, Trivy, OWASP ZAP",
            "chatbot": "Streamlit IA pour questions sécurité"
        },
        "security_showcase": {
            "vulnerable_endpoints": [
                "/search/{query} - SQL injection",
                "/load_data - Pickle deserialization",
                "/run/{command} - Command injection"
            ],
            "secure_endpoints": [
                "/secure/search/{query} - Parametrized queries",
                "/secure/load - JSON instead of pickle",
                "/secure/run/{command} - Command validation"
            ]
        },
        "sonarqube_integration": {
            "status": "Active",
            "project": "kwtar-elhai_projet_devsecops",
            "purpose": "Détection automatique des vulnérabilités à chaque commit"
        }
    }

@app.get("/api/test")
def api_test():
    """Test simple de l'API"""
    return {
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "available_endpoints": [
            "/ - Racine",
            "/health - Santé de l'API",
            "/search/{query} - ⚠️ VULNÉRABLE SQL injection",
            "/secure/search/{query} - ✅ SÉCURISÉ",
            "/load_data - ⚠️ VULNÉRABLE Pickle",
            "/secure/load - ✅ SÉCURISÉ JSON",
            "/run/{command} - ⚠️ VULNÉRABLE Command injection",
            "/secure/run/{command} - ✅ SÉCURISÉ",
            "/devsecops/info - Info projet",
            "/items - Gestion items"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)