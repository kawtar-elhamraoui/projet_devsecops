import sqlite3
import pickle
import subprocess
from fastapi import FastAPI, HTTPException
from datetime import datetime
import json
from typing import List, Optional
import uuid
from pydantic import BaseModel

app = FastAPI(title="DevSecOps Demo API", version="2.0.0")

# ========== DÉFINITION DU MODÈLE ==========
class Item(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
# ==========================================

# Initialiser une base SQLite
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
    cursor.execute("INSERT OR IGNORE INTO products (name, price) VALUES ('Laptop', 999.99)")
    cursor.execute("INSERT OR IGNORE INTO products (name, price) VALUES ('Phone', 499.99)")
    conn.commit()
    conn.close()

init_db()

# ========== ENDPOINTS DE BASE ==========

@app.get("/")
def read_root():
    return {"message": "API DevSecOps - Test SAST SonarQube", "version": "2.0.0"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# ========== 3 VULNÉRABILITÉS POUR TESTS SAST ==========

# 1. VULNÉRABILITÉ: INJECTION SQL
@app.get("/vuln/sql/{product_name}")
def sql_injection(product_name: str):
    """⚠️ VULNÉRABLE: Injection SQL - S2068 dans SonarQube"""
    conn = sqlite3.connect("test.db")
    # CONCATÉNATION DIRECTE - DÉTECTÉ PAR SONARQUBE
    query = f"SELECT * FROM products WHERE name = '{product_name}'"
    cursor = conn.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    return {
        "vulnerability": "SQL Injection",
        "query": query,
        "results": results,
        "sonarqube_rule": "S2068: SQL queries should not be vulnerable to injection attacks"
    }

# 2. VULNÉRABILITÉ: COMMAND INJECTION
@app.get("/vuln/command/{cmd_param}")
def command_injection(cmd_param: str):
    """⚠️ VULNÉRABLE: Command Injection - S2076 dans SonarQube"""
    # SHELL=True AVEC INPUT UTILISATEUR - DÉTECTÉ PAR SONARQUBE
    command = f"echo {cmd_param}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    return {
        "vulnerability": "Command Injection",
        "command": command,
        "output": result.stdout,
        "sonarqube_rule": "S2076: OS commands should not be vulnerable to injection attacks"
    }

# 3. VULNÉRABILITÉ: DÉSÉRIALISATION NON SÉCURISÉE
@app.post("/vuln/deserialize")
def insecure_deserialization(data: str):
    """⚠️ VULNÉRABLE: Insecure Deserialization - S5145 dans SonarQube"""
    try:
        # PICKLE AVEC DONNÉES UTILISATEUR - DÉTECTÉ PAR SONARQUBE
        deserialized_data = pickle.loads(data.encode('utf-8'))
        return {
            "vulnerability": "Insecure Deserialization",
            "data": str(deserialized_data),
            "sonarqube_rule": "S5145: Deserialization of untrusted data should be avoided"
        }
    except Exception as e:
        return {"error": str(e)}

# ========== VERSIONS SÉCURISÉES ==========

@app.get("/secure/sql/{product_name}")
def secure_sql_search(product_name: str):
    """✅ SÉCURISÉ: Pas d'injection SQL"""
    if not product_name.isalnum():
        raise HTTPException(status_code=400, detail="Invalid product name")
    
    conn = sqlite3.connect("test.db")
    cursor = conn.execute("SELECT * FROM products WHERE name = ?", (product_name,))
    results = cursor.fetchall()
    conn.close()
    
    return {
        "method": "Parameterized query",
        "results": results,
        "security": "✅ Safe from SQL injection"
    }

@app.get("/secure/command/{cmd}")
def secure_command(cmd: str):
    """✅ SÉCURISÉ: Pas de command injection"""
    allowed = ["echo", "date", "pwd"]
    if cmd not in allowed:
        raise HTTPException(status_code=400, detail=f"Command not allowed. Allowed: {allowed}")
    
    result = subprocess.run([cmd], shell=False, capture_output=True, text=True)
    
    return {
        "method": "Command validation + shell=False",
        "output": result.stdout,
        "security": "✅ Safe from command injection"
    }

@app.post("/secure/deserialize")
def secure_deserialize(data: str):
    """✅ SÉCURISÉ: JSON au lieu de pickle"""
    try:
        parsed = json.loads(data)
        return {
            "method": "JSON deserialization",
            "data": parsed,
            "security": "✅ Safe from arbitrary code execution"
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

# ========== ENDPOINTS POUR SONARQUBE TEST ==========

@app.get("/sonarqube/test")
def sonarqube_test_endpoints():
    """Liste des endpoints pour tester SonarQube"""
    return {
        "project": "SonarQube SAST Test",
        "vulnerable_endpoints": {
            "sql_injection": {
                "url": "/vuln/sql/{product_name}",
                "method": "GET",
                "example": "/vuln/sql/Laptop' OR '1'='1",
                "sonarqube_rule": "S2068"
            },
            "command_injection": {
                "url": "/vuln/command/{cmd_param}",
                "method": "GET",
                "example": "/vuln/command/test; ls -la",
                "sonarqube_rule": "S2076"
            },
            "insecure_deserialization": {
                "url": "/vuln/deserialize",
                "method": "POST",
                "example": "Post pickle serialized data",
                "sonarqube_rule": "S5145"
            }
        },
        "secure_endpoints": {
            "sql": "/secure/sql/{product_name}",
            "command": "/secure/command/{cmd}",
            "deserialize": "/secure/deserialize"
        },
        "test_scenarios": [
            "1. Exécuter l'analyse SonarQube",
            "2. Vérifier les 3 vulnérabilités détectées",
            "3. Comparer avec les endpoints sécurisés"
        ]
    }

@app.get("/api/info")
def api_info():
    """Information sur l'API de test"""
    return {
        "purpose": "Test SAST avec SonarQube",
        "vulnerabilities": 3,
        "sonarqube_rules": [
            "S2068 - SQL Injection",
            "S2076 - Command Injection", 
            "S5145 - Insecure Deserialization"
        ],
        "usage": "Utiliser pour démontrer la détection automatique de vulnérabilités"
    }

# Gestion simple d'items (sans vulnérabilité)
items_db = []

@app.get("/items", response_model=List[Item])
def get_items():
    return items_db

@app.post("/items")
def create_item(name: str, description: Optional[str] = None):
    item = Item(
        id=str(uuid.uuid4()),
        name=name,
        description=description
    )
    items_db.append(item)
    return item

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)