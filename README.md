# Portfolio Analytics Engine

Agent financier base sur LangChain avec outils metier (base de donnees, finance, calculs, web search, portefeuille, Python REPL), interface CLI, interface Streamlit et API REST.

## 1) Prerequis

- Python 3.10+
- Un compte OpenAI (cle API)
- Optionnel: un compte Tavily (cle API) pour la recherche web A3

## 2) Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Configuration

Creer un fichier `.env` a la racine du projet:

```env
OPENAI_API_KEY=...
TAVILY_API_KEY=...
```

Notes:
- `OPENAI_API_KEY` est obligatoire.
- `TAVILY_API_KEY` est optionnel (si absent, l'agent fonctionne sans outil web Tavily).

Le fichier `.env.example` est fourni sans cles reelles.

## 4) Initialiser la base

```bash
python init_db.py
```

Cette commande cree `database.db` et insere les donnees initiales clients/produits.

## 5) Lancer le projet

### A) Mode CLI (menu scenarios)

```bash
python main.py
```

### B) Mode Streamlit (C1)

```bash
streamlit run app.py
```

Fonctionnalites UI:
- Champ de saisie en bas
- Historique de conversation
- Sidebar avec outils disponibles
- Bouton de reset conversation

### C) Mode API REST (D1)

```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Healthcheck:

```bash
curl http://127.0.0.1:8000/health
```

Question agent:

```bash
curl -X POST http://127.0.0.1:8000/api/agent/query \
	-H "Content-Type: application/json" \
	-d '{"query":"Quel est le solde du client C001 ?"}'
```

## 6) Structure du projet

```text
agent.py                 # Construction de l'agent et outils
main.py                  # Interface CLI menu scenarios
app.py                   # Interface Streamlit
api.py                   # API FastAPI (D1)
init_db.py               # Initialisation SQLite
tools/                   # Outils metier
requirements.txt
.env.example
```