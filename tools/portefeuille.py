import yfinance as yf


def _parse_lignes_portefeuille(input_str: str) -> list[tuple[str, float]]:
    lignes = []
    elements = [e.strip() for e in input_str.split("|") if e.strip()]
    if not elements:
        raise ValueError("Entrée vide. Format attendu : SYMBOLE:QUANTITE|SYMBOLE:QUANTITE")

    for element in elements:
        if ":" not in element:
            raise ValueError(f"Format invalide pour '{element}'. Utilisez SYMBOLE:QUANTITE")
        symbole, quantite = element.split(":", 1)
        symbole = symbole.strip().upper()
        try:
            qty = float(quantite.strip())
        except ValueError as exc:
            raise ValueError(f"Quantité invalide pour '{symbole}': {quantite}") from exc
        if qty <= 0:
            raise ValueError(f"La quantité doit être positive pour '{symbole}'")
        lignes.append((symbole, qty))
    return lignes


def _snapshot_ticker(symbole: str) -> tuple[float, float]:
    ticker = yf.Ticker(symbole)
    hist = ticker.history(period="5d", interval="1d")
    if hist.empty:
        raise ValueError(f"Aucune donnée de marché pour '{symbole}'")

    hist = hist.dropna(subset=["Close"])
    if hist.empty:
        raise ValueError(f"Données de clôture indisponibles pour '{symbole}'")

    cours = float(hist.iloc[-1]["Close"])
    if len(hist) >= 2:
        precedent = float(hist.iloc[-2]["Close"])
    else:
        precedent = cours

    return cours, precedent


def calculer_portefeuille(input_str: str) -> str:
    """
    Calcule la valeur d'un portefeuille au format: SYMBOLE:QUANTITE|SYMBOLE:QUANTITE
    Exemple: AAPL:10|MSFT:5|TSLA:2
    """
    try:
        lignes = _parse_lignes_portefeuille(input_str)
    except ValueError as exc:
        return f"Erreur de format: {exc}"

    total_actuel = 0.0
    total_precedent = 0.0
    resultats = []

    for symbole, qty in lignes:
        try:
            cours, precedent = _snapshot_ticker(symbole)
        except Exception:
            return f"Symbole invalide ou données indisponibles pour '{symbole}'."

        valeur_actuelle = cours * qty
        valeur_precedente = precedent * qty
        variation_montant = valeur_actuelle - valeur_precedente
        variation_pct = (variation_montant / valeur_precedente * 100) if valeur_precedente else 0.0

        total_actuel += valeur_actuelle
        total_precedent += valeur_precedente
        resultats.append(
            (
                symbole,
                qty,
                cours,
                valeur_actuelle,
                variation_montant,
                variation_pct,
            )
        )

    variation_totale_montant = total_actuel - total_precedent
    variation_totale_pct = (variation_totale_montant / total_precedent * 100) if total_precedent else 0.0

    lignes_txt = ["Analyse du portefeuille :"]
    for symbole, qty, cours, valeur, var_amt, var_pct in resultats:
        tendance = "📈" if var_amt >= 0 else "📉"
        lignes_txt.append(
            f"- {symbole} x {qty:g} | Cours: {cours:.2f} $ | Valeur: {valeur:,.2f} $ "
            f"| Variation jour: {tendance} {var_amt:+,.2f} $ ({var_pct:+.2f}%)"
        )

    tendance_total = "📈" if variation_totale_montant >= 0 else "📉"
    lignes_txt.append(f"Valeur totale: {total_actuel:,.2f} $")
    lignes_txt.append(
        f"Variation globale du jour: {tendance_total} {variation_totale_montant:+,.2f} $ "
        f"({variation_totale_pct:+.2f}%)"
    )
    return "\n".join(lignes_txt)
