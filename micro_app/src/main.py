import sqlite3
import pickle
import subprocess
from fastapi import FastAPI, HTTPException
from datetime import datetime
import json

app = FastAPI(title="Test API Sécurité", version="1.0.0")

# Initialiser une base SQLite pour les tests
def init_db():
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT
        ) 
    """)
    cursor.execute("INSERT OR IGNORE INTO users (username, email) VALUES ('admin', 'admin@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (username, email) VALUES ('user', 'user@example.com')")
    conn.commit()
    conn.close()

init_db()

# ========== ENDPOINTS VULNÉRABLES ==========

@app.get("/vuln/sql/{user_input}")
def sql_injection(user_input: str):
    """⚠️ VULNÉRABLE : Injection SQL"""
    conn = sqlite3.connect("test.db")
    # VULNÉRABLE : concaténation directe
    cursor = conn.execute(f"SELECT * FROM users WHERE username = '{user_input}'")
    results = cursor.fetchall()
    conn.close()
    
    response = {
        "vulnerability": "SQL Injection",
        "query": f"SELECT * FROM users WHERE username = '{user_input}'",
        "results": results,
        "example_exploit": "Essayez avec: admin' OR '1'='1"
    }
    
    # Aide DAST à détecter
    if "' OR '" in user_input.upper() and len(results) > 1:
        response["warning"] = "MULTIPLE_USERS_RETURNED"
    
    return response

@app.post("/vuln/deserialize")
def pickle_deserialize(data: str):
    """⚠️ VULNÉRABLE : Désérialisation pickle"""
    try:
        # VULNÉRABLE : pickle avec données utilisateur
        loaded = pickle.loads(data.encode())
        return {
            "vulnerability": "Pickle Deserialization",
            "data": str(loaded),
            "risk": "Code execution possible",
            "secure_alternative": "Utiliser json.loads()"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/vuln/command/{cmd}")
def command_injection(cmd: str):
    """⚠️ VULNÉRABLE : Command Injection"""
    # VULNÉRABLE : shell=True avec input utilisateur
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    response = {
        "vulnerability": "Command Injection",
        "command": cmd,
        "output": result.stdout[:100],
        "error": result.stderr,
        "example_exploit": "Essayez avec: ls; cat /etc/passwd"
    }
    
    # Aide DAST à détecter
    if ";" in cmd or "&&" in cmd:
        response["shell_metacharacters"] = True
    
    return response

# ========== ENDPOINTS SÉCURISÉS ==========

@app.get("/secure/sql/{user_input}")
def secure_sql(user_input: str):
    """✅ SÉCURISÉ : Requête paramétrée"""
    conn = sqlite3.connect("test.db")
    cursor = conn.execute("SELECT * FROM users WHERE username = ?", (user_input,))
    results = cursor.fetchall()
    conn.close()
    
    return {
        "security": "SQL sécurisé avec paramètres",
        "results": results
    }

@app.post("/secure/deserialize")
def secure_deserialize(data: str):
    """✅ SÉCURISÉ : JSON au lieu de pickle"""
    try:
        loaded = json.loads(data)
        return {
            "security": "JSON sécurisé",
            "data": loaded
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

@app.get("/secure/command")
def secure_command():
    """✅ SÉCURISÉ : Commandes prédéfinies uniquement"""
    # Liste blanche de commandes autorisées
    allowed_commands = {
        "date": ["date"],
        "uptime": ["uptime"],
        "whoami": ["whoami"]
    }
    
    return {
        "security": "Commandes sécurisées (liste blanche)",
        "allowed": list(allowed_commands.keys())
    }

# ========== ENDPOINTS UTILES ==========

@app.get("/")
def root():
    return {
        "api": "Test de sécurité API - DevSecOps",
        "description": "API avec vulnérabilités intentionnelles pour démonstration",
        "vulnerabilities": [
            "GET /vuln/sql/{input} - Injection SQL",
            "POST /vuln/deserialize - Désérialisation pickle",
            "GET /vuln/command/{cmd} - Command injection"
        ],
        "secure": [
            "GET /secure/sql/{input} - SQL paramétré",
            "POST /secure/deserialize - JSON sécurisé",
            "GET /secure/command - Commandes liste blanche"
        ]
    }

@app.get("/health")
def health():
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/demo/dast/{input}")
def dast_demo_endpoint(input: str):
    """Endpoint spécial pour démontrer DAST"""
    
    if input == "safe":
        return {"status": "safe", "message": "Normal operation"}
    
    elif "' OR '" in input:
        return {
            "status": "vulnerable",
            "warning": "SQL_INJECTION_DETECTED",
            "input": input,
            "debug": "This would be dangerous in production!",
            "risk": "HIGH"
        }
    
    elif ";" in input or "&&" in input:
        return {
            "status": "vulnerable", 
            "warning": "COMMAND_INJECTION_DETECTED",
            "input": input,
            "debug": "Shell commands detected!",
            "risk": "CRITICAL"
        }
    
    return {"status": "processed", "input": input}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)