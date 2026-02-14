# ===================================================
# EVALUATION DE NOS QUESTIONS POSÉES À NOTRE SYSTÈME
# ===================================================
# ======================
# Libraires nécessaires
# ======================
import os
import sys
import csv
import logging
import json

# Ajout du dossier racine au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports
from utils.config import (CSV_FILE, SEARCH_K)
from utils.vector_store import VectorStoreManager
from utils.retrieval import Retrieval
from utils.creation_llm import (prompt_llm, generer_reponse, list_for_api)
# ==========================
# Initialisation du logging
# ==========================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# ===========================
# Les 15 questions à évaluer
# ===========================
questions_reponses = [

    # --- NIVEAU 1 : Questions faciles (Récupération directe de valeur) ---
    {
        "n": "Question simple",
        "i": "Q1",
        "q": "Quel est le nombre total de points (PTS) marqués par Shai Gilgeous-Alexander ?",
        "a": "Shai Gilgeous-Alexander a marqué un total de 2485 points durant la saison."
    },
    {
        "n": "Question simple",
        "i": "Q2",
        "q": "Combien de matchs (GP) Anthony Edwards a-t-il disputés cette saison ?",
        "a": "Anthony Edwards a disputé 79 matchs au cours de la saison."
    },
    {
        "n": "Question simple",
        "i": "Q3",
        "q": "Quel est le pourcentage de réussite au tir (FG%) de Giannis Antetokounmpo ?",
        "a": "Giannis Antetokounmpo affiche un pourcentage de réussite au tir de 60.1%."
    },
    {
        "n": "Question simple",
        "i": "Q4",
        "q": "Quel est le nombre total de passes décisives (AST) réalisées par Tyrese Haliburton ?",
        "a": "Tyrese Haliburton a délivré un total de 672 passes décisives durant la saison."
    },
    {
        "n": "Question simple",
        "i": "Q5",
        "q": "Pour quelle équipe (Team) joue Nikola Jokić ?",
        "a": "Nikola Jokić joue pour les Denver Nuggets (DEN)."
    },

    # --- NIVEAU 2 : Questions intermédiaires (Comparaisons simples) ---
    {
        "n": "Question intermédiaire",
        "i": "Q6",
        "q": "Quel joueur a marqué le plus de points entre Anthony Edwards et Nikola Jokić ?",
        "a": "Anthony Edwards a marqué plus de points qu'Nikola Jokić, avec 2180 points contre 2072."
    },
    {
        "n": "Question intermédiaire",
        "i": "Q7",
        "q": "Quel joueur a joué le plus de matchs entre Shai Gilgeous-Alexander et Giannis Antetokounmpo ?",
        "a": "Shai Gilgeous-Alexander a joué plus de matchs avec 76 rencontres contre 67 pour Giannis Antetokounmpo."
    },
    {
        "n": "Question intermédiaire",
        "i": "Q8",
        "q": "Qui affiche le meilleur pourcentage de réussite au tir (FG%) entre Stephen Curry et Anthony Edwards ?",
        "a": "Stephen Curry affiche un meilleur pourcentage de réussite au tir avec 44.8% contre 44.7% pour Anthony Edwards."
    },
    {
        "n": "Question intermédiaire",
        "i": "Q9",
        "q": "Quel joueur a distribué le plus de passes décisives entre Shai Gilgeous-Alexander et Tyrese Haliburton ?",
        "a": "Tyrese Haliburton a distribué plus de passes décisives avec 672 contre 486 pour Shai Gilgeous-Alexander."
    },
    {
        "n": "Question intermédiaire",
        "i": "Q10",
        "q": "Combien de points Jayson Tatum a-t-il inscrits cette saison ?",
        "a": "Jayson Tatum a inscrit un total de 1930 points durant la saison."
    },

    # --- NIVEAU 3 : Questions bruitées (Langage naturel, synonymes, contexte implicite) ---
    {
        "n": "Question bruitée",
        "i": "Q11",
        "q": "On cherche le roi du scoring cette saison, quel joueur termine tout en haut du classement des points ?",
        "a": "Le meilleur marqueur de la saison est Shai Gilgeous-Alexander avec 2485 points."
    },
    {
        "n": "Question bruitée",
        "i": "Q12",
        "q": "Si tu devais établir le podium des trois attaquants les plus prolifiques de la ligue, qui seraient-ils ?",
        "a": "Les trois meilleurs marqueurs sont Shai Gilgeous-Alexander (2485 points), Anthony Edwards (2180 points) et Nikola Jokić (2072 points)."
    },
    {
        "n": "Question bruitée",
        "i": "Q13",
        "q": "Y a-t-il un joueur qui a réussi l'exploit de passer la barre des 2000 points alors qu'il a participé à moins de 70 rencontres ?",
        "a": "Giannis Antetokounmpo a inscrit plus de 2000 points avec 2037 points en seulement 67 matchs."
    },
    {
        "n": "Question bruitée",
        "i": "Q14",
        "q": "Parmi l'élite des marqueurs, qui se distingue par la plus grande efficacité au tir (meilleur FG%) ?",
        "a": "Parmi les meilleurs marqueurs, Giannis Antetokounmpo affiche le meilleur pourcentage de réussite au tir avec 60.1%."
    },
    {
        "n": "Question bruitée",
        "i": "Q15",
        "q": "Quel joueur incarne la durabilité en combinant plus de 2000 points marqués et le plus grand nombre de matchs disputés parmi les leaders ?",
        "a": "Anthony Edwards a marqué plus de 2000 points tout en jouant le plus grand nombre de matchs avec 79 rencontres."
    }
]
# =========================================================
# Définition d'une fonction main pour générer l'évaluation
# =========================================================
def main():
    logging.info("--- Chargement du RAG ---")

    # On charge notre Class qui va générer nos index
    manager = VectorStoreManager()
    if manager.index is None:
        logging.error("Index non trouvé. Lancez indexer.py.")
        return
    # On charge notre fonction de récupération des informations dans la base d'index
    retriever = Retrieval(manager)
    # On retourne le template du prompt système
    system_template = prompt_llm()

    # =======================
    # Gestion du fichier CSV
    # =======================
    # On vérifie que le fichier existe
    file_exists = os.path.exists(CSV_FILE)
    
    logging.info("--- Démarrage de l'évaluation ---")

    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # En-tête de notre fichier qui va être construit
        if not file_exists:
            writer.writerow([
                "type des questions", # Indique la difficulté des questions
                "id",                   # Le numéro de la question
                "question",             # La question
                "ground_truths",        # La réponse attendue
                "answer",               # La réponse du LLM
                "contexts",             # Requis pour Ragas (les éléments de page_content)
                "source_scores"         # Requis pour Ragas (document retrouvé + score)
            ])

        for item in questions_reponses:
            n = item['n']
            i = item["i"]
            q = item["q"]
            a = item["a"]
            
            logging.info(f"Traitement : {q}")   

            # 1. Recherche
            search_results = retriever.search(q, k=SEARCH_K)
            
            # A. Colonne 'contexts' pour Ragas (Liste simple de strings)
            list_contexts = [res['text'] for res in search_results]

            # B. Colonne 'source_scores' (JSON avec Score et Document)
            # On construit une liste simple de dictionnaires
            metadata_summary = []
            for idx, res in enumerate(search_results):
                metadata_summary.append({
                    "num doc":res["metadata"].get('chunk_id_in_doc'),
                    "document": res['metadata'].get('filename', 'Inconnu'),
                    "score": round(res['score'], 2) 
                })
            
            # On transforme cette liste en chaîne JSON
            json_metadata = json.dumps(metadata_summary, ensure_ascii=False)

            # C. Contexte pour le LLM (String concaténée)
            from utils.creation_llm import context
            if not search_results:
                context_str = "Aucune information trouvée."
            else:
                context_str = context(search_results, q)

            # 2. Génération
            # On récupère la question et le context recherché
            final_prompt = system_template.format(context_str=context_str, question=q)
            # Transformation du texte en objet ChatMessage technique
            messages = list_for_api(final_prompt)
            # Génération de la réponse du LLM
            response_bot = generer_reponse(messages)

            logging.info(f"Réponse : {response_bot[:50]}...")

            # 3. Sauvegarde
            writer.writerow([
                n,
                i,
                q,
                a,
                response_bot,
                list_contexts,
                json_metadata   
            ])

    logging.info(f"Terminé ! Résultats dans {CSV_FILE}")

if __name__ == "__main__":
    main()