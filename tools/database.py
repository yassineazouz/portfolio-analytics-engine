
# Cet outil simule une base de données relationnelle contenant des informations
# sur les clients et les produits d'une PME. Il permet à l'agent de répondre à
# des questions du type : «Quel est le solde du compte de Marie Dupont ?» ou «Combien coûte le produit X ?»

# cree une base de données relationnelle avec des clients et des produits pour une PME fictive avec meme structure que les donnees ci dessous.

CLIENTS = {
    "C001": {
        "nom": "Marie Dupont",
        "email": "marie.dupont@email.fr",
        "ville": "Paris",
        "solde_compte": 15420.50,
        "type_compte": "Premium",
        "date_inscription": "2021-03-15",
        "achats_total": 8750.00
    },
    "C002": { "nom": "Jean Martin",    "solde_compte": 3200.00,  "type_compte": "Standard" },
    "C003": { "nom": "Sophie Bernard", "solde_compte": 28900.00, "type_compte": "VIP"      },
    "C004": { "nom": "Lucas Petit",    "solde_compte": 750.00,   "type_compte": "Standard" }
}

PRODUITS = {
    "P001": { "nom": "Ordinateur portable Pro", "prix_ht": 899.00, "stock": 45  },
    "P002": { "nom": "Souris ergonomique",       "prix_ht": 49.90,  "stock": 120 },
    "P003": { "nom": "Bureau réglable",           "prix_ht": 350.00, "stock": 18  },
    "P004": { "nom": "Casque audio sans fil",    "prix_ht": 129.00, "stock": 67  },
    "P005": { "nom": "Écran 27 pouces 4K",       "prix_ht": 549.00, "stock": 30  }
}

def rechercher_client(query: str) -> str:
    """Recherche un client par nom ou par identifiant."""
    query = query.strip()
    if query.upper() in CLIENTS:
        client = CLIENTS[query.upper()]
        return f"Client : {client['nom']} | Solde : {client['solde_compte']:.2f} € | Type de compte : {client['type_compte']}"
    for cid, client in CLIENTS.items():
        if query.lower() in client['nom'].lower():
            return f"Client : {client['nom']} | Solde : {client['solde_compte']:.2f} € | Type de compte : {client['type_compte']}"
    return f"Aucun client trouvé pour : '{query}'"

def rechercher_produit(query: str) -> str:
    """Recherche un produit par nom ou identifiant. Retourne prix HT, TVA, prix TTC, stock."""
    query = query.strip()
    if query.upper() in PRODUITS:
        produit = PRODUITS[query.upper()]
        tva = produit['prix_ht'] * 0.20
        prix_ttc = produit['prix_ht'] + tva
        return (f"Produit : {produit['nom']} | Prix HT : {produit['prix_ht']:.2f} € "
                f"| TVA : {tva:.2f} € | Prix TTC : {prix_ttc:.2f} € | Stock : {produit['stock']}")
    for pid, produit in PRODUITS.items():
        if query.lower() in produit['nom'].lower():
            tva = produit['prix_ht'] * 0.20
            prix_ttc = produit['prix_ht'] + tva
            return (f"Produit : {produit['nom']} | Prix HT : {produit['prix_ht']:.2f} € "
                    f"| TVA : {tva:.2f} € | Prix TTC : {prix_ttc:.2f} € | Stock : {produit['stock']}")
    return f"Aucun produit trouvé pour : '{query}'"

def lister_tous_les_clients(query: str = "") -> str:
    """Retourne la liste complète de tous les clients."""
    result = "Liste des clients :\n"
    for cid, client in CLIENTS.items():
        result += f"  {cid} : {client['nom']} | {client['type_compte']} | Solde : {client['solde_compte']:.2f} €\n"
    return result


