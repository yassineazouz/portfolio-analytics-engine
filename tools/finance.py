# Cet outil récupère des cours de marché réels via yfinance
# pour les actions et les cryptomonnaies.

import yfinance as yf

ACTIONS = {
    "AAPL": "AAPL",
    "MSFT": "MSFT",
    "GOOGL": "GOOGL",
    "LVMH": "MC.PA",   # LVMH sur Euronext Paris
    "TSLA": "TSLA",
    "AIR": "AIR.PA",   # Airbus sur Euronext Paris
}

CRYPTOS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
}


def _formater_volume(volume: int) -> str:
    """Formate un volume lisible avec séparateurs."""
    return f"{volume:,}".replace(",", " ")


def _snapshot_marche(yf_symbol: str) -> tuple[float, float, int]:
    """Retourne (cours, variation_pct, volume) à partir des données yfinance."""
    ticker = yf.Ticker(yf_symbol)
    historique = ticker.history(period="5d", interval="1d")

    if historique.empty:
        raise ValueError("Aucune donnée disponible")

    historique = historique.dropna(subset=["Close"])
    if historique.empty:
        raise ValueError("Données de clôture indisponibles")

    derniere_ligne = historique.iloc[-1]
    cours = float(derniere_ligne["Close"])
    volume = int(derniere_ligne.get("Volume", 0) or 0)

    precedent = None
    if len(historique) >= 2:
        precedent = float(historique.iloc[-2]["Close"])
    else:
        fast_info = getattr(ticker, "fast_info", None)
        if fast_info:
            precedent = fast_info.get("previous_close")
            if precedent is not None:
                precedent = float(precedent)

    if not precedent:
        variation_pct = 0.0
    else:
        variation_pct = ((cours - precedent) / precedent) * 100

    return cours, variation_pct, volume


def obtenir_cours_action(symbole: str) -> str:
    """Retourne le cours réel d'une action avec variation du jour et volume."""
    symbole = symbole.strip().upper()
    yf_symbol = ACTIONS.get(symbole)

    if not yf_symbol:
        return f"Action '{symbole}' non trouvée."

    try:
        cours, variation_pct, volume = _snapshot_marche(yf_symbol)
    except Exception:
        return f"Données indisponibles pour l'action '{symbole}' (symbole invalide ou API indisponible)."

    tendance = "📈" if variation_pct >= 0 else "📉"
    return (
        f"{symbole} {tendance} : {cours:.2f} $ ({variation_pct:+.2f}%)"
        f" | Volume : {_formater_volume(volume)}"
    )


def obtenir_cours_crypto(symbole: str) -> str:
    """Retourne le cours réel d'une cryptomonnaie avec variation du jour et volume."""
    symbole = symbole.strip().upper()
    yf_symbol = CRYPTOS.get(symbole)

    if not yf_symbol:
        return f"Crypto '{symbole}' non trouvée."

    try:
        cours, variation_pct, volume = _snapshot_marche(yf_symbol)
    except Exception:
        return f"Données indisponibles pour la crypto '{symbole}' (symbole invalide ou API indisponible)."

    tendance = "📈" if variation_pct >= 0 else "📉"
    return (
        f"{symbole} {tendance} : {cours:.2f} $ ({variation_pct:+.2f}%)"
        f" | Volume : {_formater_volume(volume)}"
    )
















