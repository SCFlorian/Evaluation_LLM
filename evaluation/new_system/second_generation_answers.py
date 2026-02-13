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
import time

# Configuration & Chemins
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)
PAUSE_SECONDS = 20
# Imports du repo
from scripts.chat import ChatPipeline
from rag.config import CSV_FILE

# =======================
# Configuration des logs
# =======================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# ========================
# On charge notre chatbot
# ========================
try:
    chatbot = ChatPipeline()
except Exception as e:
    logging.error(f"Erreur d'initialisation du Chatbot : {e}")
    chatbot = None

# ===========================
# Les 15 questions à évaluer
# ===========================
questions_reponses = [

    # --- NIVEAU 1 : Questions faciles (valeurs directes) ---

    {"n":"Question simple","i": "Q1","q": "Quel est le nombre total de points (PTS) marqués par Shai Gilgeous-Alexander ?","a": "Shai Gilgeous-Alexander a marqué un total de 2485 points durant la saison."},
    {"n":"Question simple","i": "Q2","q": "Combien de matchs (GP) Anthony Edwards a-t-il disputés cette saison ?","a": "Anthony Edwards a disputé 79 matchs au cours de la saison."},
    {"n":"Question simple","i": "Q3","q": "Quel est le pourcentage de réussite au tir de Giannis Antetokounmpo ?","a": "Giannis Antetokounmpo affiche un pourcentage de réussite au tir de 60.1%."},
    {"n":"Question simple","i": "Q4","q": "Quel est le nombre total de passes décisives (AST) réalisées par Tyrese Haliburton ?","a": "Tyrese Haliburton a délivré un total de 672 passes décisives durant la saison."},
    {"n":"Question simple","i": "Q5","q": "Pour quelle équipe (Team) joue Nikola Jokić ?","a": "Nikola Jokić joue pour les Denver Nuggets (DEN)."},
    # --- NIVEAU 2 : Questions intermédiaires (comparaison simple) ---
    {"n":"Question compliquée","i": "Q6","q": "Quel joueur a marqué le plus de points entre Anthony Edwards et Nikola Jokić ?","a": "Anthony Edwards a marqué plus de points qu'Nikola Jokić, avec 2180 points contre 2072."},
    {"n":"Question compliquée","i": "Q7","q": "Quel joueur a joué le plus de matchs entre Shai Gilgeous-Alexander et Giannis Antetokounmpo ?","a": "Shai Gilgeous-Alexander a joué plus de matchs avec 76 rencontres contre 67 pour Giannis Antetokounmpo."},
    {"n":"Question compliquée","i": "Q8","q": "Qui affiche le meilleur pourcentage de réussite au tir (FG%) entre Stephen Curry et Anthony Edwards ?","a": "Stephen Curry affiche un meilleur pourcentage de réussite au tir avec 44.8% contre 44.7% pour Anthony Edwards."},
    {"n":"Question compliquée","i": "Q9","q": "Quel joueur a distribué le plus de passes décisives entre Shai Gilgeous-Alexander et Tyrese Haliburton ?","a": "Tyrese Haliburton a distribué plus de passes décisives avec 672 contre 486 pour Shai Gilgeous-Alexander."},
    {"n":"Question compliquée","i": "Q10","q": "Combien de points Jayson Tatum a-t-il inscrits cette saison ?","a": "Jayson Tatum a inscrit un total de 1930 points durant la saison."},
    # --- NIVEAU 3 : Questions plus difficiles (classement / analyse simple) ---
    {"n":"Question bruitée","i":"Q11","q":"Parmi les joueurs ayant dépassé les 2000 points, lequel a joué le moins de matchs ?","a":"Giannis Antetokounmpo est celui qui a joué le moins de matchs avec 67 tout en dépassant les 2000 points."},
    {"n":"Question bruitée","i":"Q12","q":"Quel joueur combine plus de 2000 points et un pourcentage de réussite au tir supérieur à 55% ?","a":"Giannis Antetokounmpo est le seul joueur à combiner plus de 2000 points et un FG en pourcentage supérieur à 55%."},
    {"n":"Question bruitée","i":"Q13","q":"Si l’on exclut les joueurs ayant disputé plus de 75 matchs, qui est le meilleur marqueur restant ?","a":"En excluant les joueurs à plus de 75 matchs, Shai Gilgeous-Alexander reste le meilleur marqueur avec 2485 points."},
    {"n":"Question bruitée","i":"Q14","q":"Quel joueur marque en moyenne le plus de points par match parmi ceux ayant joué moins de 70 matchs ?","a":"Giannis Antetokounmpo est celui qui marque le plus par match parmi les joueurs à moins de 70 matchs."},
    {"n":"Question bruitée","i":"Q15","q":"Un analyste affirme que le meilleur marqueur est aussi celui ayant joué le plus de matchs. Cette affirmation est-elle correcte ?","a":"Non, le meilleur marqueur est Shai Gilgeous-Alexander (2485 points), mais celui qui a joué le plus de matchs est Anthony Edwards avec 79 matchs."},
    # --- NIVEAU 4 : Questions sur Reddit ---
    {"n":"Question reddit","i": "Q16","q": "Quelle est la franchise la plus ancienne de la NBA selon le fil 'TodayILearned' et quel était son nom d'origine ?","a": "La franchise la plus ancienne est les Sacramento Kings, fondés en 1923 sous le nom de Rochester Seagrams."},
    {"n":"Question reddit","i": "Q17","q": "Qu'a noté Luka Doncic concernant l'avantage du terrain dans les séries de playoffs récentes ?","a": "Luka Doncic a noté que c'est la première fois qu'il aura l'avantage du terrain dans une série de playoffs."},
    {"n":"Question reddit","i": "Q18","q": "Pourquoi certains fans considèrent-ils que l'affrontement entre les deux meilleures équipes statistiques est ennuyeux ?","a": "À cause d'un biais médiatique et d'un mauvais marketing de la NBA qui préfère les concours de popularité au basket pur."}
    ]

# ===============================================
# Lancement de la génération des réponses du LLM
# ===============================================
def main():
    logging.info("--- Chargement du RAG ---")
    if not chatbot:
        logging.error("Le chatbot n'est pas initialisé. Arrêt.")
        return

    # Vérification si le fichier existe déjà pour gérer l'en-tête
    file_exists = os.path.exists(CSV_FILE)
    
    logging.info(f"--- Démarrage de l'évaluation vers {CSV_FILE} ---")

    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # En-tête (seulement si le fichier est nouveau)
        if not file_exists:
            writer.writerow([
                "type des questions",
                "id",
                "question",
                "ground_truths",
                "answer",
                "contexts",
                "source_scores"
            ])

        for item in questions_reponses:
            n = item['n']
            i = item["i"]
            q = item["q"]
            a = item["a"]
            
            logging.info(f"Traitement {i}: {q}")   

            # 1. Appel du Chatbot
            try:
                result = chatbot.process_question(q)
            except Exception as e:
                logging.error(f"Erreur sur la question {i}: {e}")
                continue

            # 2. Récupération de la réponse et préparation des sources pour Ragas
            response_bot = result['answer']
            
            ragas_contexts = []
            metadatas = []

            # Sécurisation
            sources = result.get('sources', [])

            for source in sources:
                # Cas 1 : SQL
                if source.get('type') == 'database':
                    txt_data = f"Données SQL : {str(source.get('data'))}"
                    ragas_contexts.append(txt_data)
                    metadatas.append({"source": "SQL Database"})
    
                # Cas 2 : PDF
                elif source.get('type') == 'pdf':
                    ragas_contexts.append(source.get('content', ''))
                    # On récupère les métadonnées du PDF si elles existent
                    metadatas.append(source.get('metadata', {}))
                
            time.sleep(PAUSE_SECONDS)
            logging.info(f"Réponse générée : {response_bot[:50]}...")

            # 3. Sauvegarde dans le CSV
            # On utilise json.dumps pour que les listes soient bien formatées dans une seule case CSV
            writer.writerow([
                n,
                i,
                q,
                a,                      # Ground Truth
                response_bot,           # Answer du chatbot
                json.dumps(ragas_contexts), # Contexts (liste convertie en string JSON)
                json.dumps(metadatas)       # Source Scores / Metadata
            ])

    logging.info(f" Terminé ! Résultats sauvegardés dans {CSV_FILE}")

if __name__ == "__main__":
    main()