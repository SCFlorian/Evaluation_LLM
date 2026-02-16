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
PAUSE_SECONDS = 30
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
    {"n":"Question simple","i": "Q6","q": "Quelle est la franchise la plus ancienne de la NBA selon le fil 'TodayILearned' et quel était son nom d'origine ?","a": "La franchise la plus ancienne est les Sacramento Kings, fondés en 1923 sous le nom de Rochester Seagrams."},

    # --- NIVEAU 2 : Questions intermédiaires (comparaison) ---
    {"n":"Question compliquée","i": "Q7","q": "Quel joueur a marqué le plus de points entre Anthony Edwards et Nikola Jokić ?","a": "Anthony Edwards a marqué plus de points qu'Nikola Jokić, avec 2180 points contre 2072."},
    {"n":"Question compliquée","i": "Q8","q": "Quel joueur a joué le plus de matchs entre Shai Gilgeous-Alexander et Giannis Antetokounmpo ?","a": "Shai Gilgeous-Alexander a joué plus de matchs avec 76 rencontres contre 67 pour Giannis Antetokounmpo."},
    {"n":"Question compliquée","i": "Q9","q": "Qui affiche le meilleur pourcentage de réussite au tir (FG%) entre Stephen Curry et Anthony Edwards ?","a": "Stephen Curry affiche un meilleur pourcentage de réussite au tir avec 44.8% contre 44.7% pour Anthony Edwards."},
    {"n":"Question compliquée","i": "Q10","q": "Quel joueur a distribué le plus de passes décisives entre Shai Gilgeous-Alexander et Tyrese Haliburton ?","a": "Tyrese Haliburton a distribué plus de passes décisives avec 672 contre 486 pour Shai Gilgeous-Alexander."},
    {"n":"Question compliquée","i": "Q11","q": "Combien de points Jayson Tatum a-t-il inscrits cette saison ?","a": "Jayson Tatum a inscrit un total de 1930 points durant la saison."},
    {"n":"Question compliquée","i": "Q12","q": "Sur Reddit, des fans expliquent qu'une finale entre les deux meilleures équipes statistiques serait un 'snoozefest'. Pourquoi les médias de la NBA sont-ils accusés de provoquer ce désintérêt ? Et qui a marqué le plus de points (PTS) entre Jayson Tatum et Shai Gilgeous-Alexander ?","a": "Les médias sont accusés de privilégier un concours de popularité ('popularity contest') et de promouvoir les superstars plutôt que le pur niveau de basketball. C'est Shai Gilgeous-Alexander (2485 PTS) qui a marqué plus de points que Jayson Tatum (1930 PTS)."},
    {"n":"Question compliquée","i": "Q13","q": "Qu'a noté Luka Doncic concernant l'avantage du terrain dans les séries de playoffs récentes ?","a": "Luka Doncic a noté que c'est la première fois qu'il aura l'avantage du terrain dans une série de playoffs."},
    # --- NIVEAU 3 : Questions plus difficiles (classement) ---
    {"n":"Question bruitée","i":"Q14","q":"Je regardais un classement des meilleurs scoreurs récents et j’ai remarqué que plusieurs joueurs avaient dépassé les 2000 points cette saison. Mais comme certains ont joué plus de matchs que d’autres, je me demandais : parmi ces gros scoreurs, lequel a atteint ce total tout en ayant disputé le moins de matchs ?","a":"Giannis Antetokounmpo est celui qui a joué le moins de matchs avec 67 tout en dépassant les 2000 points."},
    {"n":"Question bruitée","i":"Q15","q":"Je lisais des débats sur les meilleures équipes de la conférence Est des années 90, et je me posais une question : selon un post Reddit, quel joueur des Pacers est considéré comme la première option offensive la plus efficace de l'histoire des playoffs NBA ?","a": "Selon les discussions sur Reddit, c'est Reggie Miller qui est considéré comme la première option offensive la plus efficace de l'histoire des playoffs NBA."},
    {"n":"Question bruitée","i":"Q16","q":"Je comparais récemment les performances de plusieurs scoreurs cette saison, mais je voulais éviter les joueurs qui ont joué énormément de matchs, car cela peut gonfler les totaux. Si on ne considère que les joueurs ayant disputé 75 matchs ou moins, quel joueur reste le meilleur marqueur de la saison ?","a":"En excluant les joueurs ayant disputé plus de 75 matchs, Nikola Jokić est le meilleur marqueur restant avec 2072 points."},
    {"n":"Question bruitée","i":"Q17","q":"Quel joueur marque en moyenne le plus de points par match parmi ceux ayant joué moins de 70 matchs ?","a":"Giannis Antetokounmpo est celui qui marque le plus par match parmi les joueurs à moins de 70 matchs."},
    {"n":"Question bruitée","i":"Q18","q":"Un analyste affirme que le meilleur marqueur est aussi celui ayant joué le plus de matchs. Cette affirmation est-elle correcte ?","a":"Non, le meilleur marqueur est Shai Gilgeous-Alexander (2485 points), mais celui qui a joué le plus de matchs est Anthony Edwards avec 79 matchs."},
    {"n":"Question bruitée","i": "Q19","q": "Un utilisateur Reddit déclare : 'Ant's been a machine as expected' en parlant d'Anthony Edwards. Comment juge-t-il les performances de ce joueur ? Et qui a inscrit le plus de points (PTS) au total entre Anthony Edwards et Jalen Brunson ?","a": "Il estime que le joueur répond parfaitement aux attentes et joue comme une machine. C'est Anthony Edwards (2180 PTS) qui a marqué le plus de points, devant Jalen Brunson (1690 PTS)."},
    {"n":"Question bruitée","i": "Q20","q": "Sur Reddit, un fan de Duke qualifie le duo d'Orlando de 'absolute dogs'. Pourquoi pense-t-il qu'ils sont parfaitement taillés pour les playoffs ? Et qui a joué le plus de matchs entre Franz Wagner et Paolo Banchero ?","a": "Il pense qu'ils sont taillés pour les playoffs grâce à leur capacité à créer des tirs et à rivaliser défensivement. C'est Franz Wagner (60 matchs) qui a joué plus de matchs (GP) que Paolo Banchero (46 matchs)."}
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