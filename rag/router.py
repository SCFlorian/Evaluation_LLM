# MISE EN PLACE DU ROUTEUR POUX CHOIX DE LA RECUPERATION DES DONNEES
# =======================
# Librairies nécessaires
# =======================
import sys, os
# Imports LangChain
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
# Configuration & Chemins
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import du repo
from rag.config import GROQ_API_KEY, MODEL_NAME

# ==================================================================
# Class regoupant les fonctions afin de choisir quelle base choisir
# ==================================================================
class Router:
    def __init__(self):
        """Initialise le routeur (le cerveau qui trie les questions)."""
        # On utilise le modèle configuré
        self.llm = ChatGroq(
            model_name=MODEL_NAME, 
            groq_api_key=GROQ_API_KEY,
            temperature=0 # Zéro créativité
        )

    def route_query(self, question: str) -> str:
        """
        Analyse la question et retourne : 'SQL', 'VECTOR' ou 'BOTH'.
        """
        # ==========
        # Le prompt
        # ==========
        template = """
        Tu es un expert en classification de questions pour un assistant NBA.
        Ton rôle est d'orienter la question vers la bonne source de données.

        SOURCES DISPONIBLES :

        1. "SQL" : Pour les STATISTIQUES PURES, les RECORDS et les FAITS SIMPLES.
           - Utilise ceci pour : Moyennes, totaux, classements, âges, équipes actuelles.
           - Mots-clés : "Combien", "Score", "Stats", "Meilleur marqueur", "Qui a le plus de...".
           - Ex: "Combien de points a Lebron ?", "Qui est le meilleur rebondeur ?", "Dans quelle équipe joue Curry ?"
           - Si la question demande un classement, un "meilleur", un "top", ou une exclusion basée sur des chiffres (matchs, points), C'EST DU SQL.
            Même si le mot "restant" est utilisé.

        2. "VECTOR" : Pour le TEXTE, l'HISTOIRE, les RÈGLES et les CONDITIONS SPÉCIFIQUES.
           - Utilise ceci pour : Règlements, explications ("pourquoi", "comment"), avis de fans, rumeurs.
           - IMPORTANT : Si une question demande "Qui a gagné..." avec une CONDITION NARRATIVE ou un CONTEXTE HISTORIQUE (ex: "sans avantage du terrain", "le plus jeune MVP", "après une blessure", "le plus petit joueur"), c'est du VECTOR. La base SQL ne contient que des noms et des chiffres, pas ces détails.
           - Ex: "Quelles sont les règles des playoffs ?", "Quelle équipe a gagné en 1995 sans l'avantage du terrain ?", "Que pensent les fans de Gobert ?"

        3. "BOTH" : Uniquement si la question demande CLAIREMENT deux choses distinctes (Chiffre + Texte).
           - Ex: "Donne moi les stats de Wembanyama et une analyse de son impact médiatique."

        Instructions :
        - Analyse la question ci-dessous.
        - Réponds UNIQUEMENT par un seul mot : SQL, VECTOR, ou BOTH.

        Question utilisateur : {question}
        Catégorie :
        """

        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            decision = chain.invoke({"question": question})
            # Nettoyage (enlève les espaces et met en majuscules)
            clean_decision = decision.strip().upper()
            
            # Sécurité supplémentaire : si le LLM bavarde, on coupe
            if "SQL" in clean_decision: return "SQL"
            if "BOTH" in clean_decision: return "BOTH"
            if "VECTOR" in clean_decision: return "VECTOR"
            
            return clean_decision
            
        except Exception as e:
            # En cas d'erreur technique, on renvoie VECTOR par défaut
            print(f"Erreur Routeur: {e}")
            return "VECTOR"

# ================
# Test du routeur
# ================
if __name__ == "__main__":
    router = Router()
    
    questions_test = [
        "Quel est le joueur qui a le plus de points ?",              # -> SQL
        "Que disent les journaux sur la performance de Gobert ?",     # -> VECTOR
        "Quelle équipe a gagné en 1995 sans l'avantage du terrain ?", # -> VECTOR
        "Donne moi l'âge de Lebron et une analyse de son jeu."        # -> BOTH
    ]

    print("\n--- TEST DU ROUTEUR ---")
    for q in questions_test:
        category = router.route_query(q)
        print(f"Question : '{q}' \n   -> Destination : {category}\n")