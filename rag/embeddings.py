# GÉNÉRATION DES VECTEURS
# =======================
# Librairies nécessaires
# =======================
import logging
import numpy as np
from typing import List, Dict, Tuple
# Imports LangChain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
# Import du repo
from rag.config import (
    EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
)
# =======================
# Configuration des logs
# =======================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# =====================================================================================
# Class regoupant les fonctions afin de découper les documents et générer les vecteurs
# =====================================================================================
class EmbeddingService:
    def __init__(self):
        # Chargement du modèle
        logging.info(f"Chargement du modèle d'embedding local : {EMBEDDING_MODEL}...")
        self.embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, 
            chunk_overlap=CHUNK_OVERLAP
        )

    def process_documents(self, documents: List[Dict[str, any]]) -> Tuple[List[Dict], np.ndarray]:
        # Découpage
        logging.info("Découpage des documents...")
        chunks_data = self._split_documents(documents)
        
        if not chunks_data:
            return [], None

        # Vectorisation
        texts = [chunk["text"] for chunk in chunks_data]
        logging.info(f"Génération des embeddings pour {len(texts)} chunks (Local)...")
        
        try:
            # embed_documents renvoie une liste de listes
            embeddings_list = self.embedding_model.embed_documents(texts)
            # Conversion en numpy array pour FAISS
            vectors = np.array(embeddings_list).astype('float32')
            return chunks_data, vectors
            
        except Exception as e:
            logging.error(f"Erreur embedding local : {e}")
            return [], None

    def _split_documents(self, documents):
        chunks = []
        for doc in documents:
            content = doc.get("page_content") if isinstance(doc, dict) else doc.page_content
            metadata = doc.get("metadata") if isinstance(doc, dict) else doc.metadata
            
            if content:
                splits = self.splitter.split_text(content)
                for split_text in splits:
                    chunks.append({"text": split_text, "metadata": metadata})
        return chunks