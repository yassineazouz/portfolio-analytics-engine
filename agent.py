import os
from pydantic import BaseModel, Field

from langchain_experimental.tools import PythonREPLTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool
from langchain_tavily import TavilySearch

from tools.api_publique import convertir_devise, obtenir_taux_du_jour
from tools.calculs import (
    calculer_interets_composes,
    calculer_marge,
    calculer_mensualite_pret,
    calculer_tva,
)
from tools.database import lister_tous_les_clients, rechercher_client, rechercher_produit
from tools.finance import obtenir_cours_action, obtenir_cours_crypto
from tools.portefeuille import calculer_portefeuille
from tools.recommandation import recommander_produits
from tools.text import (
    convertir_majuscules_minuscules,
    extraire_mots_cles,
    formater_rapport,
    resumer_texte,
)


class SingleInput(BaseModel):
    input: str = Field(..., description="Entree texte pour l'outil")


class RecommandationInput(BaseModel):
    budget: float = Field(..., description="Budget maximum en euros")
    categorie: str = Field(..., description="Categorie produit: Informatique, Mobilier, Audio, Toutes")
    type_compte: str = Field(..., description="Type de compte client: Standard, Premium, VIP")


def _single_input_tool(name: str, func, description: str) -> StructuredTool:
    def _runner(input: str) -> str:
        return func(input)

    return StructuredTool.from_function(
        name=name,
        func=_runner,
        description=description,
        args_schema=SingleInput,
    )


def _recommander_produits_struct(budget: float, categorie: str, type_compte: str) -> str:
    return recommander_produits(f"{budget},{categorie},{type_compte}")


tools = [
    _single_input_tool(
        "rechercher_client",
        rechercher_client,
        "Recherche un client par nom ou ID (ex: C001). Retourne solde, type de compte, historique achats.",
    ),
    _single_input_tool(
        "rechercher_produit",
        rechercher_produit,
        "Recherche un produit par nom ou ID. Retourne prix HT, TVA, prix TTC, stock.",
    ),
    _single_input_tool(
        "cours_action",
        obtenir_cours_action,
        "Cours boursier d'une action. Entree: symbole majuscule ex AAPL, MSFT, TSLA, LVMH, AIR.",
    ),
    _single_input_tool(
        "cours_crypto",
        obtenir_cours_crypto,
        "Cours d'une crypto. Entree: symbole ex BTC, ETH, SOL, BNB, DOGE.",
    ),
    _single_input_tool(
        "calculer_tva",
        calculer_tva,
        "Calcule TVA et prix TTC. Entree: prix_ht,taux ex 100,20.",
    ),
    _single_input_tool(
        "calculer_interets",
        calculer_interets_composes,
        "Interets composes. Entree: capital,taux_annuel,annees ex 10000,5,3.",
    ),
    _single_input_tool(
        "calculer_marge",
        calculer_marge,
        "Marge commerciale. Entree: prix_vente,cout_achat ex 150,80.",
    ),
    _single_input_tool(
        "calculer_mensualite",
        calculer_mensualite_pret,
        "Mensualite pret. Entree: capital,taux_annuel,mois ex 200000,3.5,240.",
    ),
    _single_input_tool(
        "calculer_portefeuille",
        calculer_portefeuille,
        "Calcule la valeur d'un portefeuille boursier avec cours reels. Entree: SYMBOLE:QUANTITE|SYMBOLE:QUANTITE.",
    ),
    _single_input_tool(
        "convertir_devise",
        convertir_devise,
        "Conversion de devises en temps reel (API Frankfurter). Entree: montant,DEV_SOURCE,DEV_CIBLE ex 100,USD,EUR.",
    ),
    _single_input_tool(
        "resumer_texte",
        resumer_texte,
        "Resume un texte et donne des statistiques. Entree: texte complet.",
    ),
    _single_input_tool(
        "formater_rapport",
        formater_rapport,
        "Formate en rapport. Entree: Cle1:Val1|Cle2:Val2.",
    ),
    _single_input_tool(
        "extraire_mots_cles",
        extraire_mots_cles,
        "Extrait les mots-cles d'un texte. Entree: texte complet.",
    ),
    StructuredTool.from_function(
        name="recommander_produits",
        func=_recommander_produits_struct,
        description=(
            "Recommandations produits. Entree structuree: budget, categorie, type_compte. "
            "Exemple: budget=300, categorie=Informatique, type_compte=Premium."
        ),
        args_schema=RecommandationInput,
    ),
]


def _construire_outil_tavily():
    """Construit l'outil Tavily seulement si la cle API est disponible."""
    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        return None

    outil = TavilySearch(max_results=5, topic="finance")
    outil.description = (
        "Recherche web en temps reel (actualites financieres, infos entreprises, tendances de marche). "
        "A utiliser pour les questions ouvertes ou l'actualite recente non couverte par les autres outils."
    )
    return outil


def _construire_outil_python_repl() -> PythonREPLTool:
    python_repl = PythonREPLTool()
    python_repl.description = (
        "Execute du code Python pour des calculs complexes ou traitements "
        "de donnees non couverts par les autres outils. "
        "Entree: code Python valide sous forme de chaine."
    )
    # ATTENTION SECURITE : cet outil execute du code arbitraire.
    # Ne jamais utiliser en production sans sandbox.
    return python_repl


def creer_agent():
    """Cree et retourne un agent LangChain avec memoire conversationnelle."""
    from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
    from langchain_classic.memory import ConversationBufferMemory
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Tu es un assistant financier. Tu utilises les outils disponibles quand necessaire et tu reponds clairement.",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    outils_agent = list(tools)
    outils_agent.append(_construire_outil_python_repl())

    tavily_tool = _construire_outil_tavily()
    if tavily_tool is not None:
        outils_agent.append(tavily_tool)

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = create_openai_tools_agent(llm=llm, tools=outils_agent, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=outils_agent,
        memory=memory,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
    )


def interroger_agent(agent, question: str):
    """Envoie une question a l'agent et affiche la reponse finale."""
    print(f"\n{'=' * 60}")
    print(f"Question : {question}")
    print("=" * 60)
    result = agent.invoke({"input": question})
    print(f"\nReponse finale : {result['output']}")
    return result
