import streamlit as st
from dotenv import load_dotenv

from agent import creer_agent
from init_db import initialiser_base

load_dotenv()


@st.cache_resource
def get_agent():
    initialiser_base()
    return creer_agent()


def main():
    st.set_page_config(page_title="Agent Financier", page_icon="📊", layout="wide")
    st.title("Agent Financier")
    st.caption("Posez une question, l'agent choisit automatiquement les outils nécessaires.")

    agent = get_agent()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.sidebar.title("Outils disponibles")
    for tool in agent.tools:
        st.sidebar.markdown(f"- **{tool.name}**")
    st.sidebar.divider()
    if st.sidebar.button("Réinitialiser la conversation", use_container_width=True):
        st.session_state.messages = []
        agent.memory.clear()
        st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Écrivez votre question...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Analyse en cours..."):
                try:
                    result = agent.invoke({"input": question})
                    reponse = str(result.get("output", ""))
                except Exception as exc:
                    reponse = f"Erreur : {exc}"
            st.markdown(reponse)

        st.session_state.messages.append({"role": "assistant", "content": reponse})


if __name__ == "__main__":
    main()
