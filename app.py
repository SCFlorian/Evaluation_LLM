# LANCEMENT DE L'API EN LOCAL
# =======================
# Librairies nécessaires
# =======================
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import os
from pydantic import BaseModel
import uvicorn
# ==================
# Imports du projet
# ==================
from scripts.chat import response
from scripts.build_index import run_indexing
from scripts.generation_db import generate_sql_db
from rag.config import INPUT_DIR

# ========================
# Activation de notre API
# ========================

app = FastAPI(title="SportSee - Prototype chatbot")
# ====================
# Modèle d'entrée API
# ====================
class Question(BaseModel):
    question: str
# ============================================
# Gestion de l'erreur 404 (Route inexistante)
# ============================================
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error_code": 404,
            "message": "Cette route n'existe pas.",
            "detail": f"L'URL '{request.url.path}' est inconnue.",
            "suggestion": "Essayez plutôt /ask ou /rebuild ou encore /health"
        }
    )
# ===============
# Routes simples
# ===============
@app.get("/health")
def health_check():
    return {"status":"OK", "messages":"API opéationnelle"}

# ================================================
# Fonction de génération de la réponse du chatbot
# ================================================
@app.post("/ask")
def speak_to_chatbot(data: Question):
    try:
        question = "Quel est le meilleur marqueur ?"
        answer = response(data.question)
        return {"answer":answer}
    except Exception as e:
        return {
            "status": "Erreur",
            "message": str(e)
        }
    
# ==================================================
# Fonction afin de reconstruire la base vectorielle
# ==================================================
@app.post("/rebuild_index")
def rebuild_index_vectoriel():
    """ Si on ajoute des nouveaux documents en PDF, on peut générer des 
    nouveaux embeddings"""
    try:
        run_indexing(INPUT_DIR)

        return {
            "status":"Succès",
            "message":"Nouveaux documents transformés en index"
        }
    except Exception as e:
        return {
            "status": "Erreur",
            "message": str(e)
        }

# ==================================================
# Fonction afin de reconstruire la base SQL
# ==================================================
@app.post('/rebuild_SQL_Base')
def rebuild_sql_base():
    """ Si on ajoute des nouveaux éléments dans la BDD,
    on peut la géénrer de nouveau ici"""
    try:
        generate_sql_db()

        return {
            "status":"Succès",
            "message":"Tables de la BDD à jour"
        }
    except Exception as e:
        return {
            "status": "Erreur",
            "message": str(e)
        }

# =========================
# Lancement local
# =========================
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7860)