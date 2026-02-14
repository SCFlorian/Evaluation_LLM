# GENERATION DU CHAT
# =======================
# Librairies nécessaires
# =======================
import logging
import sys, os
import time
import logfire
# ======================
# CONFIGURATION LOGFIRE
# ======================
# Cela configure tout automatiquement
logfire.configure()
logfire.instrument_pydantic()
logfire.instrument_system_metrics()
# Configuration & Chemins
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Imports du repo
from rag.router import Router
from database.sql_tool import SQLTool
from rag.retrieval import RetrievalService
from rag.creation_llm import generer_reponse, list_for_api
from database.preprocessing_excel import dict_def_stats
from tests.validation_pydantic import InputData, OutputData
from pydantic import ValidationError

# =======================
# Configuration des logs
# =======================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# =========================================================
# Class regoupant les fonctions afin de générer la réponse
# =========================================================
class ChatPipeline:
    """
    Classe principale qui gère toute la logique de conversation.
    Elle charge les modèles une seule fois au démarrage.
    """
    def __init__(self):
        logging.info("Initialisation du ChatPipeline (Chargement des modèles)...")
        try:
            # 1. Le Routeur (Choisit entre SQL et Texte)
            self.router = Router()
            # 2. L'outil SQL (Interroge la BDD)
            self.sql_tool = SQLTool()
            # 3. Le Retriever (Cherche dans les PDF)
            self.retriever = RetrievalService()
            logging.info("ChatPipeline prêt !")
        except Exception as e:
            logging.error(f"Erreur critique lors du chargement du Pipeline : {e}")
            raise e
    @logfire.instrument("Traitement Pipeline: {question}")
    def process_question(self, question: str):
        """
        Traite la question sans planter sur les variables avec Pydantic.
        """
        # ==========================================
        # 1. VALIDATION ENTRÉE (Check Pydantic)
        # ==========================================
        try:
            InputData(question=question)
        except ValidationError:
            # Si invalide, on renvoie une réponse d'erreur tout de suite
            return {
                "answer": "Erreur : La question est vide ou trop courte.",
                "route": "ERREUR",
                "context": "", "definitions": {}, "sources": []
            }
        # Chargement du fichier excel pour les métadonnées (définition des colonnes stats)
        df_dict_clean = dict_def_stats()
        start_time = time.time()
        logging.info(f" Nouvelle question : {question}")
        with logfire.span("Router Decision"):
        # 1. ROUTAGE
            route = self.router.route_query(question)
            logging.info(f"Décision du routeur : {route}")

        context_text = ""
        
        # =============================
        # Initialisation des variables
        # =============================
        sql_section = ""
        doc_section = ""
        used_definitions = {}
        sources_finales = []

        try:
            # =========
            # BLOC SQL
            # =========
            if route in ["SQL", "BOTH"]:
                raw_data = self.sql_tool.run_query(question)
                used_definitions = df_dict_clean
                glossary_text = ", ".join([f"{k}={v}" for k, v in df_dict_clean.items()])
                sources_finales.append({"type": "database", "data": raw_data})
                
                sql_section = (
                    f"DONNÉES SQL (SOURCE OFFICIELLE) : {raw_data}\n"
                    f"CONSIGNE TECHNIQUE : Ces données sont le résultat brut d'une requête SQL exécutée spécifiquement pour répondre à la question : '{question}'.\n"
                    f"AIDE GLOSSAIRE : {glossary_text}\n"
                    f"RÈGLE D'INTERPRÉTATION : \n"
                    f"- Si la question demande un classement ou un superlatif, et que tu ne vois que quelques résultats, c'est NORMAL (LIMIT SQL appliqué).\n"
                    f"- N'indique pas que les données viennent de la base SQL ou autre.\n"
                    f"- Ne dis JAMAIS 'je ne peux pas savoir'. Fais confiance à ce résultat.\n"
                )
            # ============
            # BLOC VECTOR
            # ============
            if route in ["VECTOR", "BOTH"]:
                # 1. On récupère la liste des documents
                with logfire.span("Vector Retrieval"):
                    docs = self.retriever.retrieve(question)
                
                # 2. On prépare le texte pour le LLM
                doc_raw = "\n\n".join([d.page_content for d in docs])
                
                # 3. On boucle sur la liste pour remplir les sources
                for d in docs:
                    sources_finales.append({
                        "type": "pdf", 
                        "content": d.page_content, 
                        "metadata": d.metadata
                    })

                doc_section = f"INFORMATIONS DOCUMENTAIRES (CONTEXTE) :\n{doc_raw}"
            # =================
            # ASSEMBLAGE FINAL
            # =================
            if route == "SQL":
                context_text = sql_section 
            
            elif route == "VECTOR":
                context_text = (
                    f"{doc_section}\n"
                    "CONSIGNE : Réponds uniquement à partir de ces textes."
                )

            elif route == "BOTH":
                context_text = (
                    f"{sql_section}\n"
                    f"--------------------------------------------------\n"
                    f"{doc_section}\n"
                    f"CONSIGNE DE SYNTHÈSE : Le SQL a toujours raison sur les chiffres. Utilise le texte pour expliquer ou commenter."
                )

        except Exception as e:
            logging.error(f"Erreur technique ({route}) : {e}")
            context_text = "Une erreur est survenue lors de la récupération des données."

        # 3. GÉNÉRATION
        logging.info("Génération de la réponse...")
        api_messages = list_for_api(context_text, question)
        final_answer = generer_reponse(api_messages)

        elapsed = time.time() - start_time
        logging.info(f"Réponse générée en {elapsed:.2f}s")

        # ======================================
        # 2. VALIDATION SORTIE (Check Pydantic)
        # ======================================
        try:
            OutputData(answer=final_answer, route=route, sources=sources_finales)
        except ValidationError as e:
            logging.error(f"ATTENTION : Erreur format sortie détectée : {e}")

        return {
            "answer": final_answer,
            "route": route,
            "context": context_text,
            "definitions": used_definitions,
            "sources": sources_finales
        }
# =================        
# Instance Globale
# =================
try:
    chatbot = ChatPipeline()
except Exception:
    chatbot = None

def response(prompt: str):
    if chatbot:
        result = chatbot.process_question(prompt)
        return result["answer"]
    else:
        return "Erreur : Le chatbot n'est pas initialisé."

# =====
# TEST
# =====
if __name__ == "__main__":
    print("\n--- TEST DU CHAT PIPELINE ---")
    
    q1 = "Quelle est la franchise la plus ancienne de la NBA selon le fil 'TodayILearned' et quel était son nom d'origine ?"
    print(f"\nQ: {q1}")
    res1 = chatbot.process_question(q1)
    print(f"Route: {res1['route']}")
    print(f"R: {res1['answer']}")

    print("-" * 20)
