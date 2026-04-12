import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "database.db"


CLIENTS = [
    ("C001", "Marie Dupont", "marie.dupont@email.fr", "Paris", 15420.50, "Premium", "2021-03-15", 8750.00),
    ("C002", "Jean Martin", None, None, 3200.00, "Standard", None, None),
    ("C003", "Sophie Bernard", None, None, 28900.00, "VIP", None, None),
    ("C004", "Lucas Petit", None, None, 750.00, "Standard", None, None),
]

PRODUITS = [
    ("P001", "Ordinateur portable Pro", 899.00, 45),
    ("P002", "Souris ergonomique", 49.90, 120),
    ("P003", "Bureau réglable", 350.00, 18),
    ("P004", "Casque audio sans fil", 129.00, 67),
    ("P005", "Écran 27 pouces 4K", 549.00, 30),
]


def initialiser_base() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id TEXT PRIMARY KEY,
                nom TEXT NOT NULL,
                email TEXT,
                ville TEXT,
                solde_compte REAL NOT NULL,
                type_compte TEXT NOT NULL,
                date_inscription TEXT,
                achats_total REAL
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS produits (
                id TEXT PRIMARY KEY,
                nom TEXT NOT NULL,
                prix_ht REAL NOT NULL,
                stock INTEGER NOT NULL
            )
            """
        )

        cur.executemany(
            """
            INSERT OR REPLACE INTO clients
            (id, nom, email, ville, solde_compte, type_compte, date_inscription, achats_total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            CLIENTS,
        )

        cur.executemany(
            """
            INSERT OR REPLACE INTO produits
            (id, nom, prix_ht, stock)
            VALUES (?, ?, ?, ?)
            """,
            PRODUITS,
        )

        conn.commit()


if __name__ == "__main__":
    initialiser_base()
    print(f"Base initialisee: {DB_PATH}")
