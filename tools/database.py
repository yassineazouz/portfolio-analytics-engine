
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "database.db"


def _connexion() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _erreur_db() -> str:
    return "Base de donnees introuvable. Executez init_db.py pour initialiser database.db."


def rechercher_client(query: str) -> str:
    """Recherche un client par nom ou par identifiant."""
    query = query.strip()
    if not DB_PATH.exists():
        return _erreur_db()

    try:
        with _connexion() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT nom, solde_compte, type_compte
                FROM clients
                WHERE UPPER(id) = ?
                LIMIT 1
                """,
                (query.upper(),),
            )
            row = cur.fetchone()

            if row is None:
                cur.execute(
                    """
                    SELECT nom, solde_compte, type_compte
                    FROM clients
                    WHERE LOWER(nom) LIKE ?
                    ORDER BY id
                    LIMIT 1
                    """,
                    (f"%{query.lower()}%",),
                )
                row = cur.fetchone()

            if row is None:
                return f"Aucun client trouve pour : '{query}'"

            return (
                f"Client : {row['nom']} | Solde : {row['solde_compte']:.2f} € "
                f"| Type de compte : {row['type_compte']}"
            )
    except sqlite3.Error as exc:
        return f"Erreur base de donnees : {exc}"


def rechercher_produit(query: str) -> str:
    """Recherche un produit par nom ou identifiant. Retourne prix HT, TVA, prix TTC, stock."""
    query = query.strip()
    if not DB_PATH.exists():
        return _erreur_db()

    try:
        with _connexion() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT nom, prix_ht, stock
                FROM produits
                WHERE UPPER(id) = ?
                LIMIT 1
                """,
                (query.upper(),),
            )
            row = cur.fetchone()

            if row is None:
                cur.execute(
                    """
                    SELECT nom, prix_ht, stock
                    FROM produits
                    WHERE LOWER(nom) LIKE ?
                    ORDER BY id
                    LIMIT 1
                    """,
                    (f"%{query.lower()}%",),
                )
                row = cur.fetchone()

            if row is None:
                return f"Aucun produit trouve pour : '{query}'"

            prix_ht = float(row["prix_ht"])
            tva = prix_ht * 0.20
            prix_ttc = prix_ht + tva
            return (
                f"Produit : {row['nom']} | Prix HT : {prix_ht:.2f} € "
                f"| TVA : {tva:.2f} € | Prix TTC : {prix_ttc:.2f} € | Stock : {row['stock']}"
            )
    except sqlite3.Error as exc:
        return f"Erreur base de donnees : {exc}"


def lister_tous_les_clients(query: str = "") -> str:
    """Retourne la liste complète de tous les clients."""
    if not DB_PATH.exists():
        return _erreur_db()

    try:
        with _connexion() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, nom, type_compte, solde_compte
                FROM clients
                ORDER BY id
                """
            )
            rows = cur.fetchall()

            result = "Liste des clients :\n"
            for row in rows:
                result += (
                    f"  {row['id']} : {row['nom']} | {row['type_compte']} "
                    f"| Solde : {row['solde_compte']:.2f} €\n"
                )
            return result
    except sqlite3.Error as exc:
        return f"Erreur base de donnees : {exc}"


