import yfinance as yf

ACTIONS = {
    "AAPL":  "AAPL",
    "MSFT":  "MSFT",
    "GOOGL": "GOOGL",
    "LVMH":  "MC.PA",
    "TSLA":  "TSLA",
    "AIR":   "AIR.PA",
}

CRYPTOS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
}

def _snapshot(yf_symbol: str):
    hist = yf.Ticker(yf_symbol).history(period="5d", interval="1d").dropna(subset=["Close"])
    if hist.empty:
        raise ValueError("Données indisponibles")
    cours = float(hist.iloc[-1]["Close"])
    volume = int(hist.iloc[-1].get("Volume", 0) or 0)
    precedent = float(hist.iloc[-2]["Close"]) if len(hist) >= 2 else cours
    variation = ((cours - precedent) / precedent) * 100 if precedent else 0.0
    return cours, variation, volume

def _formater_volume(volume: int) -> str:
    return f"{volume:,}".replace(",", " ")

def obtenir_cours_action(symbole: str) -> str:
    symbole = symbole.strip().upper()
    if symbole not in ACTIONS:
        return f"Action '{symbole}' non trouvée. Disponibles : {', '.join(ACTIONS.keys())}"
    try:
        cours, variation, volume = _snapshot(ACTIONS[symbole])
    except Exception:
        return f"Données indisponibles pour '{symbole}'."
    tendance = "📈" if variation >= 0 else "📉"
    return f"{symbole} {tendance} : {cours:.2f} $ ({variation:+.2f}%) | Volume : {_formater_volume(volume)}"

def obtenir_cours_crypto(symbole: str) -> str:
    symbole = symbole.strip().upper()
    if symbole not in CRYPTOS:
        return f"Crypto '{symbole}' non trouvée. Disponibles : {', '.join(CRYPTOS.keys())}"
    try:
        cours, variation, volume = _snapshot(CRYPTOS[symbole])
    except Exception:
        return f"Données indisponibles pour '{symbole}'."
    tendance = "📈" if variation >= 0 else "📉"
    return f"{symbole} {tendance} : {cours:.2f} $ ({variation:+.2f}%) | Volume : {_formater_volume(volume)}"
