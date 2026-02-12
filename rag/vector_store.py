# ENREGISTREMENT DES VECTEURS
# =======================
# Librairies nécessaires
# =======================
import os
import logging
from typing import List, Dict
# Imports LangChain
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from tests.validation_pydantic import ChunkGuard
# Import du repo
from rag.embeddings import EmbeddingService
from rag.config import EMBEDDING_MODEL
# =======================
# Configuration des logs
# =======================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# ==============================================================
# Class regoupant les fonctions afin d'enregistrer les vecteurs
# ==============================================================
class VectorStoreManager:
    def __init__(self):
        self.processor = EmbeddingService()
        # On initialise le modèle d'embedding ici pour le passer à FAISS
        self.embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.index = None

    def build_index(self, documents: List[Dict[str, any]]):
        if not documents:
            logging.warning("Aucun document à indexer.")
            return

        # Préparation (Découpage + Vectorisation)
        chunks_data, vectors = self.processor.process_documents(documents)
        # ====================
        # VALIDATION PYDANTIC
        # ====================
        # On force la validation. Si un chunk est mauvais, le script s'arrête ici.
        try:
            [ChunkGuard(**chunk) for chunk in chunks_data]
            logging.info("Tous les chunks ont été validés par Pydantic.")
        except Exception as e:
            logging.error(f"ARRÊT : Données invalides détectées dans les chunks : {e}")
            return

        if not chunks_data:
            logging.error("Aucun chunk généré.")
            return

        # Création des objets "Documents" pour LangChain
        # On doit ré-assembler texte + métadonnées pour que FAISS puisse les stocker
        text_embeddings = []
        metadatas = []
        
        for i, chunk in enumerate(chunks_data):
            text = chunk["text"]
            meta = chunk["metadata"]
            text_embeddings.append((text, vectors[i]))
            metadatas.append(meta)

        logging.info(f"Construction de l'index LangChain pour {len(text_embeddings)} chunks...")

        # Création de l'index via LangChain
        # Cette méthode crée l'index compatible avec load_local
        vector_store = FAISS.from_embeddings(
            text_embeddings=text_embeddings,
            embedding=self.embedding_model,
            metadatas=metadatas
        )
        self.index = vector_store

        # Sauvegarde Standardisée
        save_folder = "vector_db"
        index_name = "faiss_index"
        
        # Crée le dossier si besoin
        os.makedirs(save_folder, exist_ok=True)
        
        logging.info(f"Sauvegarde de l'index dans {save_folder}/{index_name}...")
        vector_store.save_local(folder_path=save_folder, index_name=index_name)
        logging.info("Sauvegarde terminée avec succès.")