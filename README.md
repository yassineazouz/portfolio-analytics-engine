# Portfolio Analytics Engine

Agent conversationnel financier basé sur LangChain et GPT-4o-mini. Il utilise des outils pour interroger une base de données, récupérer des cours boursiers réels, faire des calculs financiers, et bien plus.

## Prérequis

- Python 3.10+
- Une clé API OpenAI
- (Optionnel) Une clé API Tavily pour la recherche web

## Installation

```bash
pip install -r requirements.txt
```

Créer un fichier `.env` à la racine :

```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...   # optionnel
```

## Lancement

### Terminal interactif

```bash
python main.py
```

11 scénarios sont disponibles via un menu numéroté.

### Interface Streamlit

```bash
streamlit run app.py
```

### API REST

```bash
uvicorn api:app --reload
```

Endpoint disponible : `POST http://localhost:8000/api/agent/query`

```json
{
  "query": "Quel est le cours de Apple ?"
}
```

Santé de l'API : `GET http://localhost:8000/health`

## Outils disponibles

| Outil | Description |
|---|---|
| `rechercher_client` | Cherche un client par nom ou ID dans la base SQLite |
| `rechercher_produit` | Cherche un produit par nom ou ID |
| `lister_clients` | Liste tous les clients |
| `cours_action` | Cours réel via yfinance (AAPL, MSFT, TSLA, LVMH, AIR, GOOGL) |
| `cours_crypto` | Cours réel via yfinance (BTC, ETH, SOL) |
| `calculer_portefeuille` | Valeur totale d'un portefeuille avec cours réels |
| `calculer_tva` | Calcul TVA et prix TTC |
| `calculer_interets` | Intérêts composés |
| `calculer_marge` | Marge commerciale |
| `calculer_mensualite` | Mensualité de prêt |
| `convertir_devise` | Conversion de devises via API Frankfurter |
| `resumer_texte` | Résumé et statistiques d'un texte |
| `formater_rapport` | Mise en forme d'un rapport |
| `extraire_mots_cles` | Extraction de mots-clés |
| `recommander_produits` | Recommandations selon budget et type de compte |
| `Python_REPL` | Exécution de code Python pour calculs avancés |
| `TavilySearch` | Recherche web en temps réel (si clé disponible) |

## Structure du projet

```
portfolio-analytics-engine/
├── agent.py          # Définition des outils et création de l'agent
├── app.py            # Interface Streamlit
├── api.py            # API REST FastAPI
├── main.py           # Menu interactif terminal
├── init_db.py        # Initialisation de la base SQLite
├── database.db       # Base SQLite (générée automatiquement)
├── .env              # Clés API (à créer)
└── tools/
    ├── database.py       # Accès base de données
    ├── finance.py        # Cours boursiers (yfinance)
    ├── portefeuille.py   # Calcul de portefeuille
    ├── calculs.py        # Calculs financiers
    ├── api_publique.py   # API Frankfurter (devises)
    ├── recommandation.py # Recommandations produits
    └── text.py           # Traitement de texte
```
