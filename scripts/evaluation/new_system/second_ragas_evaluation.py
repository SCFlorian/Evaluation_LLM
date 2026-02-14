# ==========================
# DEUXIEME ÉVALUATION RAGAS
# ==========================
# =======================
# Librairies nécessaires
# =======================
import os
import sys
import pandas as pd
import logging
import json
import time
from dotenv import load_dotenv
# Imports Ragas
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
# Imports LangChain 
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

# Configuration & Chemins
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)
# Import du repo
from rag.config import GROQ_API_KEY, MODEL_NAME


# ==============
# Configuration
# ==============
INPUT_CSV = "data/processed/second_eval_results_test.csv"      
OUTPUT_CSV = "data/processed/second_eval_ragas_test.csv"   
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2" 
PAUSE_SECONDS = 30                      

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def parse_json_column(x):
    """Transforme le texte JSON '[...]' en vraie liste Python."""
    try:
        if isinstance(x, list): return x
        if pd.isna(x) or x == "": return []
        return json.loads(x)
    except Exception as e:
        logging.warning(f"Erreur parsing JSON: {e}")
        return []

def main():
    # 1. Chargement du CSV
    if not os.path.exists(INPUT_CSV):
        logging.error(f" Fichier {INPUT_CSV} introuvable ! Lance d'abord generation_answers.py.")
        return

    logging.info(f" Lecture de {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV)

    # 2. Préparation des données pour Ragas
    # On convertit la colonne 'contexts' (qui est du texte JSON) en liste Python
    df['contexts'] = df['contexts'].apply(parse_json_column)
    
    # Ragas attend un dictionnaire avec ces clés précises :
    data_dict = {
        "question": df["question"].tolist(),
        "answer": df["answer"].tolist(),
        "contexts": df["contexts"].tolist(),
        "ground_truth": df["ground_truths"].tolist()
    }
    
    ragas_dataset = Dataset.from_dict(data_dict)
    logging.info(f" Dataset Ragas prêt : {len(ragas_dataset)} questions à évaluer.")

    # 3. Initialisation du "juge"
    logging.info(f" Initialisation du Juge Groq ({MODEL_NAME})...")
    
    # LLM
    llm_judge = ChatGroq(
        model_name=MODEL_NAME, 
        groq_api_key=GROQ_API_KEY,
        temperature=0 # Zéro créativité 
    )
    
    # Les Embeddings : Nécessaires pour calculer la similarité vectorielle
    embeddings_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall
    ]

    # 4. Boucle d'évaluation
    logging.info(" Démarrage de l'évaluation...")
    results_list = []
    
    for i in range(len(ragas_dataset)):
        batch = ragas_dataset.select([i])
        logging.info(f"--- Question {i+1}/{len(ragas_dataset)} ---")
        
        try:
            # On évalue cette question
            score = evaluate(
                dataset=batch,
                metrics=metrics,
                llm=llm_judge,
                embeddings=embeddings_model,
                raise_exceptions=False
            )
            # On stocke le résultat
            results_list.append(score.to_pandas())
            
            # Sécurité
            time.sleep(PAUSE_SECONDS)
            
        except Exception as e:
            logging.error(f" Erreur sur la question {i+1} : {e}")
            # On ajoute une ligne vide pour garder le bon nombre de lignes
            results_list.append(pd.DataFrame([{"error": str(e)}]))

    # 5. Fusion et sauvegarde
    if results_list:
        ragas_results_df = pd.concat(results_list, ignore_index=True)
        
        df_final = pd.concat([df, ragas_results_df], axis=1)
        
        # Sauvegarde dans un nouveau fichier
        df_final.to_csv(OUTPUT_CSV, index=False)
        logging.info(f"\n Terminé ! Les résultats complets sont dans : {OUTPUT_CSV}")
        
        # Affichage des moyennes
        print("\n=== SCORES MOYENS (GROQ) ===")
        for m in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']:
            if m in df_final.columns:
                print(f"{m}: {df_final[m].mean():.4f}")
    else:
        logging.error("Aucun résultat n'a pu être généré.")

if __name__ == "__main__":
    main()