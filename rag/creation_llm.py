# CREATION DE LA LOGIQUE DU LLM
# =======================
# Librairies nécessaires
# =======================
import logging
import time
import sys, os
# Imports LangChain pour Groq
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
# Configuration & Chemins
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import du repo
from rag.config import GROQ_API_KEY, MODEL_NAME

def generer_reponse(messages):
    """
    Envoie la conversation à Groq.
    """
    try:
        # Initialisation du client Groq
        chat = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=MODEL_NAME,
            temperature=0.3
        )
        # Appel API
        return chat.invoke(messages).content

    except Exception as e:
        logging.error(f"Erreur Groq: {e}")
        return f"Erreur lors de la génération : {str(e)}"

# =============================================================================
# Fonction avec le prompt final donné au LLM et la fonction de l'envoi à l'API
# =============================================================================
def prompt_llm(context, query):
    return f"""
    Tu es un assistant expert NBA. Utilise le contexte ci-dessous pour répondre à la question.
    Si la réponse n'est pas dans le contexte, dis que tu ne sais pas.
    
    Contexte:
    {context}
    
    Question: {query}
    """

def list_for_api(context, query):
    return [
        {"role": "system", "content": "Tu es un assistant NBA utile."},
        {"role": "user", "content": prompt_llm(context, query)}
    ]