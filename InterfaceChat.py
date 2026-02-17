# INTERACTION AVEC LE CHATBOT VIA STREAMLIT
# =======================
# Librairies nécessaires
# =======================
import streamlit as st
import time
import sys, os
# Imports
from rag.retrieval import RetrievalService
from rag.creation_llm import generer_reponse
from scripts.chat import ChatPipeline
# On charge la réponsé du chatbot
try:
    chatbot = ChatPipeline()
except Exception:
    chatbot = None

# --- Configuration de la Page ---
st.set_page_config(page_title="Assistant NBA (Groq)", page_icon="🏀")

st.title("🏀 NBA Analyst AI")
st.caption("Propulsé par Groq (LPU) & HuggingFace")

# --- Initialisation de la Session ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "retriever" not in st.session_state:
    with st.spinner("Chargement de la mémoire vectorielle..."):
        st.session_state.retriever = RetrievalService()

# --- Affichage de l'Historique ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Interaction
if prompt := st.chat_input("Pose ta question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        status = st.status("Traitement en cours...", expanded=True)
        
        # Appel Backend
        resultat = chatbot.process_question(prompt)
        
        # Mise à jour status
        status.write(f"📍 Route utilisée : **{resultat['route']}**")
        status.write(f"📍 Dictionnaire utilisée : **{resultat['definitions']}**")
        status.update(label="Réponse prête !", state="complete", expanded=False)

        # Affichage Réponse
        st.markdown(resultat["answer"])
        st.session_state.messages.append({"role": "assistant", "content": resultat["answer"]})

