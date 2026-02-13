# =================
# EVALUATION RAGAS 
# =================
# ======================
# Librairies nécessaires
# ======================
import os
import sys
import pandas as pd
import logging
import json
import ast
import time  
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from mistralai.client import MistralClient

# Métriques Ragas
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall)

# Import de nest_asyncio pour débloquer la boucle d'événements Ragas
try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    print("Attention: 'nest_asyncio' n'est pas installé.")

# ================
# Imports du repo
# ================
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import (SEARCH_K, CSV_FILE, MODEL_NAME, MISTRAL_API_KEY, EMBEDDING_MODEL)
from datasets import Dataset

# Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# ========================================
# Définition de notre fonction principale
# ========================================
def main():
    # Chargement du CSV
    logging.info(f"Lecture de {CSV_FILE}")
    df = pd.read_csv(CSV_FILE)

    # Nettoyage des colonnes
    try:
        df['contexts'] = df['contexts'].fillna("[]").apply(ast.literal_eval)
    except Exception as e:
        logging.warning(f"Échec ast, tentative json : {e}")

    # Création du Dataset Ragas
    data_dict = {
        "question": df["question"],
        "answer": df["answer"],
        "contexts": df["contexts"],
        "ground_truth": df["ground_truths"],
        }
    ragas_dataset = Dataset.from_dict(data_dict)
    logging.info("Dataset prêt pour évaluation.")

    # Initialisation du LLM
    llm = ChatMistralAI(
            model=MODEL_NAME,
            temperature=0.1,
            api_key=MISTRAL_API_KEY
        )
    # Initialisation des Embeddings
    embeddings = MistralAIEmbeddings(
            model=EMBEDDING_MODEL,
            api_key=MISTRAL_API_KEY
        )

    # Définition des métriques
    metrics_to_evaluate = [
            faithfulness,       
            answer_relevancy,   
            context_precision,  
            context_recall,     
        ]
    logging.info(f"Métriques sélectionnées: {[m.name for m in metrics_to_evaluate]}")

    # =========================================================
    # MODIFICATION ICI : ÉVALUATION PAR BATCH AVEC PAUSE
    # =========================================================
    logging.info("\nLancement de l'évaluation Ragas (Mode Pas-à-Pas)")
    
    BATCH_SIZE = 1        # On traite 1 question à la fois
    PAUSE_SECONDS = 10    # <--- C'EST ICI QU'ON AJOUTE LE TEMPS (10 secondes de pause)
    results_list = []     # Pour stocker les résultats au fur et à mesure

    # Boucle sur le dataset
    total_questions = len(ragas_dataset)
    for i in range(0, total_questions, BATCH_SIZE):
        # On sélectionne juste un petit morceau du dataset
        batch = ragas_dataset.select(range(i, min(i + BATCH_SIZE, total_questions)))
        
        logging.info(f"Traitement de la question {i+1}/{total_questions}...")
        
        try:
            # On évalue SEULEMENT ce petit morceau
            batch_result = evaluate(
                dataset=batch,
                metrics=metrics_to_evaluate,
                llm=llm,
                embeddings=embeddings,
                raise_exceptions=False # Important : ne plante pas tout si une question échoue
            )
            # On ajoute le résultat à notre liste
            results_list.append(batch_result.to_pandas())
            
            # --- LA PAUSE CRUCIALE ---
            if i + BATCH_SIZE < total_questions: # On ne fait pas de pause après la dernière question
                logging.info(f"Pause de {PAUSE_SECONDS}s pour l'API...")
                time.sleep(PAUSE_SECONDS)
                
        except Exception as e:
            logging.error(f"Erreur sur la question {i+1} : {e}")
            # On continue quand même !

    logging.info("\n--- Évaluation Ragas terminée ---")

    # Reconstitution du DataFrame final
    if results_list:
        results_df = pd.concat(results_list, ignore_index=True)
    else:
        logging.error("Aucun résultat n'a pu être généré.")
        return

    # =========================================================
    # FIN DE LA MODIFICATION
    # =========================================================

    df_final = df.copy()
    # On ajoute les colonnes de scores
    for metric in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']:
        if metric in results_df.columns:
            # On s'assure que les index correspondent bien
            df_final[metric] = results_df[metric].values

    # Affichage pour vérifier
    pd.set_option('display.max_rows', None)
    logging.info("\n--- Aperçu des résultats finaux ---")
    cols_to_show = ['question'] + [m for m in ['faithfulness', 'answer_relevancy'] if m in df_final.columns]
    logging.info(df_final[cols_to_show].head())

    # Sauvegarde
    output_filename = "data/resultat_evaluation_ragas_test.csv" 
    df_final.to_csv(output_filename, index=False)

    logging.info(f"\nSuccès ! Les résultats enrichis sont sauvegardés dans : {output_filename}")

    # Calcul des moyennes
    logging.info("\n--- Scores Moyens ---")
    numeric_cols = [m for m in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall'] if m in df_final.columns]
    logging.info(df_final[numeric_cols].mean())

if __name__ == "__main__":
    main()