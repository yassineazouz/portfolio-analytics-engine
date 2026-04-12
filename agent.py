import os

from langchain_classic.tools import Tool
from langchain_tavily import TavilySearch
from langchain_experimental.tools import PythonREPLTool
from tools.database import lister_tous_les_clients, rechercher_client, rechercher_produit
from tools.recommandation import recommander_produits
from tools.text import formater_rapport, extraire_mots_cles, convertir_majuscules_minuscules, resumer_texte
from tools.finance import obtenir_cours_action, obtenir_cours_crypto
from tools.api_publique import convertir_devise, obtenir_taux_du_jour
from tools.calculs import calculer_tva, calculer_interets_composes, calculer_marge, calculer_mensualite_pret
from tools.portefeuille import calculer_portefeuille

tools = [
    # ── Outil 1 : Base de données ─────────────────────────────────────
    Tool(name='rechercher_client', func=rechercher_client,
         description='Recherche un client par nom ou ID (ex: C001). '
                     'Retourne solde, type de compte, historique achats.'),

    Tool(name='rechercher_produit', func=rechercher_produit,
         description='Recherche un produit par nom ou ID. '
                     'Retourne prix HT, TVA, prix TTC, stock.'),

    # ── Outil 2 : Données financières ─────────────────────────────────

    Tool(name='cours_action', func=obtenir_cours_action,
         description='Cours boursier d\'une action. '
                     'Entrée : symbole majuscule ex AAPL, MSFT, TSLA, LVMH, AIR.'),

    Tool(name='cours_crypto', func=obtenir_cours_crypto,
         description='Cours d\'une crypto. '
                     'Entrée : symbole ex BTC, ETH, SOL, BNB, DOGE.'),

    # ── Outil 3 : Calculs financiers ──────────────────────────────────

    Tool(name='calculer_tva', func=calculer_tva,
         description='Calcule TVA et prix TTC. Entrée : prix_ht,taux ex 100,20.'),

    Tool(name='calculer_interets', func=calculer_interets_composes,
         description='Intérêts composés. Entrée : capital,taux_annuel,années ex 10000,5,3.'),

    Tool(name='calculer_marge', func=calculer_marge,
         description='Marge commerciale. Entrée : prix_vente,cout_achat ex 150,80.'),

    Tool(name='calculer_mensualite', func=calculer_mensualite_pret,
         description='Mensualité prêt. Entrée : capital,taux_annuel,mois ex 200000,3.5,240.'),

    Tool(name='calculer_portefeuille', func=calculer_portefeuille,
         description='Calcule la valeur d\'un portefeuille boursier avec cours réels. '
                     'Entrée : SYMBOLE:QUANTITE|SYMBOLE:QUANTITE ex AAPL:10|MSFT:5|TSLA:2. '
                     'Retourne la valeur de chaque ligne, la valeur totale et la variation globale du jour.'),

    # ── Outil 4 : API publique ────────────────────────────────────────

    Tool(name='convertir_devise', func=convertir_devise,
         description='Conversion de devises en temps réel (API Frankfurter). '
                     'Entrée : montant,DEV_SOURCE,DEV_CIBLE ex 100,USD,EUR.'),

    # ── Outil 5 : Transformation de texte ────────────────────────────

    Tool(name='resumer_texte', func=resumer_texte,
         description='Résume un texte et donne des statistiques. Entrée : texte complet.'),

    Tool(name='formater_rapport', func=formater_rapport,
         description='Formate en rapport. Entrée : Cle1:Val1|Cle2:Val2.'),
    
    Tool(name='extraire_mots_cles', func=extraire_mots_cles,
         description='Extrait les mots-clés d\'un texte. Entrée : texte complet.'),

    # ── Outil 6 : Recommandation ─────────────────────────────────────

    Tool(name='recommander_produits', func=recommander_produits,
         description='Recommandations produits. '
                     'Entrée : budget,categorie,type_compte ex 300,Informatique,Premium. '
                     'Catégories : Informatique, Mobilier, Audio, Toutes. '
                     'Types : Standard, Premium, VIP.'),
]


def _construire_outil_tavily():
    """Construit l'outil Tavily seulement si la clé API est disponible."""
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
        "Exécute du code Python pour des calculs complexes ou traitements "
        "de données non couverts par les autres outils. "
        "Entrée : code Python valide sous forme de chaîne."
    )
     # ATTENTION SECURITE : cet outil exécute du code arbitraire.
     # Ne jamais utiliser en production sans sandbox.
    return python_repl


def creer_agent():
    """Crée et retourne un agent LangChain configuré."""
    from langchain_openai import ChatOpenAI
    from langchain_classic.agents import AgentExecutor, create_react_agent
    from langchain_classic import hub

    # Initialisation du LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,           # 0 = déterministe (résultats reproductibles)
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )

    # Chargement du prompt ReAct depuis le hub LangChain
    # Ce prompt enseigne au LLM le cycle Thought → Action → Observation
    prompt = hub.pull("hwchase17/react")

    outils_agent = list(tools)
    outils_agent.append(_construire_outil_python_repl())

    tavily_tool = _construire_outil_tavily()
    if tavily_tool is not None:
        outils_agent.append(tavily_tool)

    # Création de l'agent avec la stratégie ReAct
    agent = create_react_agent(llm=llm, tools=outils_agent, prompt=prompt)

    # Création de l'exécuteur
    agent_executor = AgentExecutor(
        agent=agent,
        tools=outils_agent,
        verbose=True,            # Affiche le raisonnement étape par étape
        max_iterations=10,       # Évite les boucles infinies
        handle_parsing_errors=True
    )
    return agent_executor


def interroger_agent(agent, question: str):
    """Envoie une question à l'agent et affiche la réponse finale."""
    print(f"\n{'='*60}")
    print(f"Question : {question}")
    print('='*60)
    result = agent.invoke({"input": question})
    print(f"\nRéponse finale : {result['output']}")
    return result
