import os
from dotenv import load_dotenv
from langchain_classic.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_experimental.tools import PythonREPLTool

from tools.database import lister_tous_les_clients, rechercher_client, rechercher_produit
from tools.recommandation import recommander_produits
from tools.text import extraire_mots_cles, formater_rapport, resumer_texte
from tools.finance import obtenir_cours_action, obtenir_cours_crypto
from tools.api_publique import convertir_devise
from tools.calculs import calculer_interets_composes, calculer_marge, calculer_mensualite_pret, calculer_tva
from tools.portefeuille import calculer_portefeuille

tools = [
    Tool(name="rechercher_client", func=rechercher_client,
         description="Recherche un client par nom ou ID (ex: C001). Retourne solde et type de compte."),
    Tool(name="rechercher_produit", func=rechercher_produit,
         description="Recherche un produit par nom ou ID. Retourne prix HT, TVA, prix TTC, stock."),
    Tool(name="lister_clients", func=lister_tous_les_clients,
         description="Liste tous les clients de la base de données."),
    Tool(name="cours_action", func=obtenir_cours_action,
         description="Cours réel d'une action en bourse. Entrée : symbole majuscule ex AAPL, MSFT, TSLA, LVMH, AIR."),
    Tool(name="cours_crypto", func=obtenir_cours_crypto,
         description="Cours réel d'une crypto. Entrée : symbole ex BTC, ETH, SOL."),
    Tool(name="calculer_tva", func=calculer_tva,
         description="Calcule TVA et prix TTC. Entrée : prix_ht,taux ex 100,20."),
    Tool(name="calculer_interets", func=calculer_interets_composes,
         description="Intérêts composés. Entrée : capital,taux_annuel,années ex 10000,5,3."),
    Tool(name="calculer_marge", func=calculer_marge,
         description="Marge commerciale. Entrée : prix_vente,cout_achat ex 150,80."),
    Tool(name="calculer_mensualite", func=calculer_mensualite_pret,
         description="Mensualité prêt. Entrée : capital,taux_annuel,mois ex 200000,3.5,240."),
    Tool(name="calculer_portefeuille", func=calculer_portefeuille,
         description="Valeur d'un portefeuille boursier réel. Entrée : SYMBOLE:QUANTITE|SYMBOLE:QUANTITE ex AAPL:10|MSFT:5."),
    Tool(name="convertir_devise", func=convertir_devise,
         description="Conversion de devises via API Frankfurter. Entrée : montant,DEV_SOURCE,DEV_CIBLE ex 100,USD,EUR."),
    Tool(name="resumer_texte", func=resumer_texte,
         description="Résume un texte. Entrée : texte complet."),
    Tool(name="formater_rapport", func=formater_rapport,
         description="Formate en rapport. Entrée : Cle1:Val1|Cle2:Val2."),
    Tool(name="extraire_mots_cles", func=extraire_mots_cles,
         description="Extrait les mots-clés d'un texte. Entrée : texte complet."),
    Tool(name="recommander_produits", func=recommander_produits,
         description="Recommandations produits. Entrée : budget,categorie,type_compte ex 300,Informatique,Premium. "
                     "Catégories : Informatique, Mobilier, Audio, Toutes. Types : Standard, Premium, VIP."),
]


def creer_agent():
    from langchain_openai import ChatOpenAI
    from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
    from langchain_classic.memory import ConversationBufferMemory

    load_dotenv()

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Tu es un assistant financier expert. Utilise les outils disponibles pour répondre avec précision."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    all_tools = list(tools)

    python_repl = PythonREPLTool()
    python_repl.description = (
        "Exécute du code Python pour des calculs complexes ou traitements "
        "de données non couverts par les autres outils. "
        "Entrée : code Python valide sous forme de chaîne."
    )
    # ATTENTION SECURITE : cet outil exécute du code arbitraire.
    # Ne jamais utiliser en production sans sandbox.
    all_tools.append(python_repl)

    if os.getenv("TAVILY_API_KEY", "").strip():
        from langchain_community.tools.tavily_search import TavilySearchResults
        tavily = TavilySearchResults(max_results=5)
        tavily.description = (
            "Recherche web en temps réel pour les actualités financières, "
            "informations sur une entreprise, cours récents non couverts par les autres outils. "
            "Utiliser pour des questions ouvertes ou d'actualité récente."
        )
        all_tools.append(tavily)

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = create_openai_tools_agent(llm=llm, tools=all_tools, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=all_tools,
        memory=memory,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
    )


def interroger_agent(agent, question: str):
    print(f"\n{'=' * 60}")
    print(f"Question : {question}")
    print("=" * 60)
    result = agent.invoke({"input": question})
    print(f"\nRéponse finale : {result['output']}")
    return result
