# RÉCUPÉRATION DES INFORMATIONS DE LA BDD
# =======================
# Librairies nécessaires
# =======================
import sys, os
import logging
# Imports LangChain pour la chaîne SQL
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
# Configuration & Chemins
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.config import DATABASE_URL, GROQ_API_KEY, MODEL_NAME

# =======================
# Configuration des logs
# =======================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# =============================================================
# Class regoupant les fonctions afin de générer la réponse SQL
# =============================================================

class SQLTool:
    def __init__(self):
        """Initialise la connexion DB et le LLM une seule fois."""
        try:
            self.db = SQLDatabase.from_uri(DATABASE_URL)
            self.llm = ChatGroq(
                model_name=MODEL_NAME, 
                groq_api_key=GROQ_API_KEY,
                temperature=0 
            )
            self.chain = self._create_chain()
            logging.info("Outil SQL initialisé (Mode Strict Guimets).")
            
        except Exception as e:
            logging.error(f"Erreur d'initialisation SQLTool : {e}")
            raise e
    
    def _get_schema(self, _):
        return self.db.get_table_info()
    # ===================================================
    # Création de la chaîne via LCEL pour la réponse SQL
    # ===================================================
    def _create_chain(self):
        # --- Prompt pour "l'agent SQL" ---
        template = """
        Tu es un expert SQL. Ta mission est de convertir la question en requête SQL valide.

        Schéma de la base :
        {table_info}

        RÈGLES CRITIQUES (A RESPECTER IMPÉRATIVEMENT) :
        1. Utilise UNIQUEMENT les tables 'player' et 'stats'.
        2. La table 'stats' a une colonne "Player" (avec majuscule) qui sert de clé de jointure vers 'player'."name".
        3. IMPORTANT : Tu dois TOUJOURS mettre les noms de tables et de colonnes entre guillemets doubles.
           - CORRECT : SELECT "name", "age" FROM "player"
           - INCORRECT : SELECT name, age FROM player
        4. Ne réponds QUE par le code SQL. Pas de blabla.

        5. RÈGLE CRUCIALE POUR LE SELECT (CONTEXTE) :
        - Ne sélectionne JAMAIS une seule colonne de chiffres.
        - Sélectionne TOUJOURS la colonne 'Player' (ou 'Team') EN PREMIER, puis la statistique demandée.

        6. RÈGLE ANTI-ERREUR (GROUPING ERROR) :
        - Si tu utilises une fonction d'agrégation (SUM, AVG, COUNT, MAX, MIN) en même temps qu'une colonne de texte (comme "Player"), tu DOIS ajouter une clause GROUP BY.
        - INCORRECT : SELECT "Player", SUM("PTS") FROM "stats" WHERE "Player" = 'Shai';
        - CORRECT   : SELECT "Player", SUM("PTS") FROM "stats" WHERE "Player" = 'Shai' GROUP BY "Player";

        Exemples :
        Q: Qui est le meilleur marqueur ?
        SQL: SELECT p."name", s."PTS" FROM "stats" s JOIN "player" p ON s."Player" = p."name" ORDER BY s."PTS" DESC LIMIT 1;

        Q: Quel est le nombre total de points de Shai ?
        SQL: SELECT "Player", SUM("PTS") FROM "stats" WHERE "Player" LIKE '%Shai%' GROUP BY "Player";

        7. RÈGLE SUPPLEMENTAIRE:
        Si la question compare deux joueurs ou plus, utilise WHERE Player IN ('Joueur1', 'Joueur2') pour récupérer les stats de TOUS les joueurs mentionnés.
        
        Question utilisateur : {question}
        SQL :
        """
        
        prompt = PromptTemplate.from_template(template)

        chain = (
            RunnablePassthrough.assign(table_info=self._get_schema)
            | prompt
            | self.llm
            | StrOutputParser()
        )
        return chain

    def _clean_sql(self, sql_text: str) -> str:
        sql_text = sql_text.replace("```sql", "").replace("```", "").strip()
        if ";" in sql_text:
            sql_text = sql_text.split(";")[0] + ";"
        return sql_text

    def run_query(self, question: str):
        print(f"\n Analyse SQL pour : '{question}'")
        try:
            generated_sql = self.chain.invoke({"question": question})
            clean_sql = self._clean_sql(generated_sql)
            print(f"SQL Généré : {clean_sql}")

            result = self.db.run(clean_sql)
            print(f"Résultat DB : {result}")
            return result

        except Exception as e:
            # On loggue l'erreur proprement
            logging.error(f"Erreur SQL : {e}")
            return f"Erreur lors de l'exécution SQL (Vérifiez les colonnes). Détail: {str(e)}"

# ==========================================
# Test direct
# ==========================================
if __name__ == "__main__":
    tool = SQLTool()
    
    q = "Quel est le meilleur marqueur avec le moins de matchs joués ?"
    tool.run_query(q)