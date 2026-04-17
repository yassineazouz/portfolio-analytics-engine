import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database.db"

def _connexion():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def rechercher_client(query: str) -> str:
    query = query.strip()
    with _connexion() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clients WHERE UPPER(id) = ? LIMIT 1", (query.upper(),))
        row = cur.fetchone()
        if row is None:
            cur.execute("SELECT * FROM clients WHERE LOWER(nom) LIKE ? LIMIT 1", (f"%{query.lower()}%",))
            row = cur.fetchone()
    if row is None:
        return f"Aucun client trouvé pour : '{query}'"
    return f"Client : {row['nom']} | Solde : {row['solde_compte']:.2f} € | Type : {row['type_compte']}"

def rechercher_produit(query: str) -> str:
    query = query.strip()
    with _connexion() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM produits WHERE UPPER(id) = ? LIMIT 1", (query.upper(),))
        row = cur.fetchone()
        if row is None:
            cur.execute("SELECT * FROM produits WHERE LOWER(nom) LIKE ? LIMIT 1", (f"%{query.lower()}%",))
            row = cur.fetchone()
    if row is None:
        return f"Aucun produit trouvé pour : '{query}'"
    prix_ht = float(row['prix_ht'])
    tva = prix_ht * 0.20
    return (f"Produit : {row['nom']} | Prix HT : {prix_ht:.2f} € "
            f"| TVA : {tva:.2f} € | Prix TTC : {prix_ht + tva:.2f} € | Stock : {row['stock']}")

def lister_tous_les_clients(query: str = "") -> str:
    with _connexion() as conn:
        rows = conn.cursor().execute("SELECT * FROM clients ORDER BY id").fetchall()
    result = "Liste des clients :\n"
    for row in rows:
        result += f"  {row['id']} : {row['nom']} | {row['type_compte']} | Solde : {row['solde_compte']:.2f} €\n"
    return result
