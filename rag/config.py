# CONFIGURATION DU PROJET
# =======================
# Librairies nécessaires
# =======================
import os
from dotenv import load_dotenv

# On charge notre .env
load_dotenv()

# --- Clés API ---
# On utilise maintenant GROQ_API_KEY
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Modèles ---
# LLM : On utilise Llama via Groq
MODEL_NAME = "llama-3.3-70b-versatile"

# Embeddings : On utilise un modèle HuggingFace 
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# --- Configuration de l'Indexation ---
INPUT_DIR = "data/raw"
VECTOR_DB_DIR = "vector_db"
FAISS_INDEX_FILE = os.path.join(VECTOR_DB_DIR, "faiss_index.idx")
DOCUMENT_CHUNKS_FILE = os.path.join(VECTOR_DB_DIR, "document_chunks.pkl")

CHUNK_SIZE = 1000  # Légèrement réduit pour le modèle d'HuggingFace
CHUNK_OVERLAP = 100
EMBEDDING_BATCH_SIZE = 32

# --- Configuration de la Recherche ---
SEARCH_K = 5

# --- Base de données SQL ---
DATABASE_DIR = "database"
DATABASE_FILE = os.path.join(DATABASE_DIR, "interactions.db")
DATABASE_URL = os.getenv("DATABASE_URL")

# --- App Config ---
APP_TITLE = "NBA Analyst AI"
NAME = "NBA"
CSV_FILE="data/processed/second_eval_results.csv"