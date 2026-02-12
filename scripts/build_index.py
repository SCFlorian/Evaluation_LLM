# ENREGISTREMENT DE NOS INDEX
# =======================
# Librairies nécessaires
# =======================
import argparse
import logging
from typing import Optional
import sys,os
# ==================
# Imports du projet
# ==================
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.config import INPUT_DIR
from rag.data_loader import load_and_parse_files
from rag.vector_store import VectorStoreManager
# ========
# Logging
# ========
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# ======================
# Fonction d'indexation
# ======================
def run_indexing(input_directory: str, data_url: Optional[str] = None):
    """Exécute le processus complet d'indexation."""
    logging.info("--- Démarrage du processus d'indexation ---")

    # --- Étape 2: Chargement et Parsing des Fichiers ---
    logging.info(f"Chargement et parsing des fichiers depuis: {input_directory}")
    documents = load_and_parse_files(input_directory)

    if not documents:
        logging.warning("Aucun document n'a été chargé ou parsé. Vérifiez le contenu du dossier d'entrée.")
        logging.info("--- Processus d'indexation terminé (aucun document traité) ---")
        return

    # --- Étape 3: Création/Mise à jour de l'index Vectoriel ---
    logging.info("Initialisation du gestionnaire de Vector Store...")
    vector_store = VectorStoreManager() # Le constructeur ne fait que charger s'il existe

    logging.info("Construction de l'index Faiss (cela peut prendre du temps)...")
    # Cette méthode va splitter, générer les embeddings, créer l'index et sauvegarder
    vector_store.build_index(documents)

    logging.info("--- Processus d'indexation terminé avec succès ---")
    logging.info(f"Nombre de documents traités: {len(documents)}")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script d'indexation pour l'application RAG")
    parser.add_argument(
        "--input-dir",
        type=str,
        default=INPUT_DIR,
        help=f"Répertoire contenant les fichiers sources (par défaut: {INPUT_DIR})"
    )
    args = parser.parse_args()

    # Génération des index
    run_indexing(args.input_dir)