from dotenv import load_dotenv
import streamlit as st

from agent import creer_agent
from init_db import initialiser_base


load_dotenv()


@st.cache_resource
def get_agent():
    """Crée l'agent une seule fois par session Streamlit."""
    initialiser_base()
    return creer_agent()


def _initialiser_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []


def _afficher_sidebar(agent) -> None:
    st.sidebar.title("Outils disponibles")
    for tool in agent.tools:
        st.sidebar.markdown(f"- **{tool.name}**")

    st.sidebar.divider()
    if st.sidebar.button("Réinitialiser la conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


def _afficher_historique() -> None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def _traiter_question(agent, question: str) -> None:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Analyse en cours..."):
            try:
                result = agent.invoke({"input": question})
                reponse = str(result.get("output", ""))
            except Exception as exc:
                reponse = f"Erreur lors de l'appel de l'agent : {exc}"
            st.markdown(reponse)

    st.session_state.messages.append({"role": "assistant", "content": reponse})


def main() -> None:
    st.set_page_config(page_title="Agent Financier", page_icon="📊", layout="wide")
    st.title("Agent Financier - Interface Streamlit")
    st.caption("Posez une question, l'agent choisit automatiquement les outils nécessaires.")

    agent = get_agent()
    _initialiser_session_state()
    _afficher_sidebar(agent)
    _afficher_historique()

    question = st.chat_input("Écrivez votre question...")
    if question:
        _traiter_question(agent, question)


if __name__ == "__main__":
    main()
