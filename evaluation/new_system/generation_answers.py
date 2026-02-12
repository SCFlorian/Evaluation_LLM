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
PAUSE_SECONDS = 5
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

    {"i": "Q1","q": "Quel est le nombre total de points (PTS) marqués par Shai Gilgeous-Alexander ?","a": "Shai Gilgeous-Alexander a marqué un total de 2485 points durant la saison."},
    {"i": "Q2","q": "Combien de matchs (GP) Anthony Edwards a-t-il disputés cette saison ?","a": "Anthony Edwards a disputé 79 matchs au cours de la saison."},
    {"i": "Q3","q": "Quel est le pourcentage de réussite au tir (FG%) de Giannis Antetokounmpo ?","a": "Giannis Antetokounmpo affiche un pourcentage de réussite au tir de 60.1%."},
    {"i": "Q4","q": "Quel est le nombre total de passes décisives (AST) réalisées par Tyrese Haliburton ?","a": "Tyrese Haliburton a délivré un total de 672 passes décisives durant la saison."},
    {"i": "Q5","q": "Pour quelle équipe (Team) joue Nikola Jokić ?","a": "Nikola Jokić joue pour les Denver Nuggets (DEN)."},
    # --- NIVEAU 2 : Questions intermédiaires (comparaison simple) ---
    {"i": "Q6","q": "Quel joueur a marqué le plus de points entre Anthony Edwards et Nikola Jokić ?","a": "Anthony Edwards a marqué plus de points qu'Nikola Jokić, avec 2180 points contre 2072."},
    {"i": "Q7","q": "Quel joueur a joué le plus de matchs entre Shai Gilgeous-Alexander et Giannis Antetokounmpo ?","a": "Shai Gilgeous-Alexander a joué plus de matchs avec 76 rencontres contre 67 pour Giannis Antetokounmpo."},
    {"i": "Q8","q": "Qui affiche le meilleur pourcentage de réussite au tir (FG%) entre Stephen Curry et Anthony Edwards ?","a": "Stephen Curry affiche un meilleur pourcentage de réussite au tir avec 44.8% contre 44.7% pour Anthony Edwards."},
    {"i": "Q9","q": "Quel joueur a distribué le plus de passes décisives entre Shai Gilgeous-Alexander et Tyrese Haliburton ?","a": "Tyrese Haliburton a distribué plus de passes décisives avec 672 contre 486 pour Shai Gilgeous-Alexander."},
    {"i": "Q10","q": "Combien de points Jayson Tatum a-t-il inscrits cette saison ?","a": "Jayson Tatum a inscrit un total de 1930 points durant la saison."},
    # --- NIVEAU 3 : Questions plus difficiles (classement / analyse simple) ---
    {"i": "Q11","q": "Quel joueur est le meilleur marqueur (PTS) de la saison selon le dataset ?","a": "Le meilleur marqueur de la saison est Shai Gilgeous-Alexander avec 2485 points."},
    {"i": "Q12","q": "Quels sont les trois meilleurs marqueurs de la saison en termes de points (PTS) ?","a": "Les trois meilleurs marqueurs sont Shai Gilgeous-Alexander (2485 points), Anthony Edwards (2180 points) et Nikola Jokić (2072 points)."},
    {"i": "Q13","q": "Quel joueur a inscrit plus de 2000 points tout en jouant moins de 70 matchs ?","a": "Giannis Antetokounmpo a inscrit plus de 2000 points avec 2037 points en seulement 67 matchs."},
    {"i": "Q14","q": "Quel joueur parmi les meilleurs marqueurs affiche le meilleur pourcentage de réussite au tir (FG%) ?","a": "Parmi les meilleurs marqueurs, Giannis Antetokounmpo affiche le meilleur pourcentage de réussite au tir avec 60.1%."},
    {"i": "Q15","q": "Quel joueur a marqué plus de 2000 points et joué le plus grand nombre de matchs parmi les meilleurs marqueurs ?","a": "Anthony Edwards a marqué plus de 2000 points tout en jouant le plus grand nombre de matchs avec 79 rencontres."},
    # --- NIVEAU 4 : Questions sur Reddit ---
    {"i": "Q_REDDIT_1","q": "Quelle est la franchise la plus ancienne de la NBA selon le fil 'TodayILearned' et quel était son nom d'origine ?","a": "La franchise la plus ancienne est les Sacramento Kings, fondés en 1923 sous le nom de Rochester Seagrams."},
    {"i": "Q_REDDIT_2","q": "Qu'a noté Luka Doncic concernant l'avantage du terrain dans les séries de playoffs récentes ?","a": "Luka Doncic a noté que c'est la première fois qu'il aura l'avantage du terrain dans une série de playoffs."},
    {"i": "Q_REDDIT_3","q": "Pourquoi certains fans considèrent-ils que l'affrontement entre les deux meilleures équipes statistiques est ennuyeux ?","a": "À cause d'un biais médiatique et d'un mauvais marketing de la NBA qui préfère les concours de popularité au basket pur."}
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
            i = item["i"]
            q = item["q"]
            a = item["a"]
            
            logging.info(f"Traitement : {q}")   

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