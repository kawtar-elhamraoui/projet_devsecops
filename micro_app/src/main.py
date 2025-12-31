from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
import uuid

app = FastAPI(title="DevSecOps Demo API", version="1.0.0")

# Modèle de données
class Item(BaseModel):
    id: str
    name: str
    description: str = None

# Base de données en mémoire
items_db = []

@app.get("/")
def read_root():
    return {"message": "API DevSecOps - Projet de Fin d'Année"}

@app.get("/items", response_model=List[Item])
def get_items():
    return items_db

@app.post("/items", response_model=Item, status_code=201)
def create_item(name: str, description: str = None):
    new_item = Item(
        id=str(uuid.uuid4()),
        name=name,
        description=description
    )
    items_db.append(new_item)
    return new_item

@app.get("/items/{item_id}")
def get_item(item_id: str):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item non trouvé")

# Endpoint avec vulnérabilité intentionnelle pour les tests
@app.get("/vulnerable/{user_input}")
def vulnerable_endpoint(user_input: str):
    # VULNÉRABLE : Injection potentielle
    return {"input": user_input, "message": "Ce endpoint est vulnérable pour les tests de sécurité"}