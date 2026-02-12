# RÉCUPÉRATION DES VECTEURS
# =======================
# Librairies nécessaires
# =======================
import logging
import time
# Imports LangChain
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
# Import du repo
from rag.config import (
    FAISS_INDEX_FILE, EMBEDDING_MODEL, SEARCH_K
)
# =======================
# Configuration des logs
# =======================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ===============================================================
# Class regoupant les fonctions afin d'effectuer la récupération
# ===============================================================
class RetrievalService:
    def __init__(self):
        self.vector_store = None
        self._load_vector_store()

    def _load_vector_store(self):
        """Charge l'index FAISS depuis le disque avec le modèle HuggingFace."""
        try:
            logging.info(f"Chargement du modèle d'embedding pour lecture : {EMBEDDING_MODEL}")
            embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
            
            logging.info(f"Chargement de l'index FAISS depuis {FAISS_INDEX_FILE}...")
            # allow_dangerous_deserialization est nécessaire pour FAISS local
            self.vector_store = FAISS.load_local(
                folder_path="vector_db", 
                embeddings=embeddings,
                index_name="faiss_index",
                allow_dangerous_deserialization=True
            )
            logging.info("Index chargé avec succès.")
        except Exception as e:
            logging.error(f"Erreur fatale lors du chargement de l'index : {e}")
            self.vector_store = None

    def retrieve(self, query: str, k: int = SEARCH_K):
        """Recherche les documents les plus proches."""
        if not self.vector_store:
            logging.warning("Impossible de chercher : Index non chargé.")
            return []
            
        try:
            # Recherche par similarité
            docs = self.vector_store.similarity_search(query, k=k)
            return docs
        except Exception as e:
            logging.error(f"Erreur lors de la recherche : {e}")
            return []