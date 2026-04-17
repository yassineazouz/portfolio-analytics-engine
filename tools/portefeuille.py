import yfinance as yf

def calculer_portefeuille(input_str: str) -> str:
    lignes = []
    for element in input_str.strip().split("|"):
        element = element.strip()
        if ":" not in element:
            return f"Format invalide : '{element}'. Utilisez SYMBOLE:QUANTITE|SYMBOLE:QUANTITE"
        symbole, quantite = element.split(":", 1)
        try:
            qty = float(quantite.strip())
        except ValueError:
            return f"Quantité invalide pour '{symbole.strip()}'"
        lignes.append((symbole.strip().upper(), qty))

    total = 0.0
    total_precedent = 0.0
    resultats = []

    for symbole, qty in lignes:
        hist = yf.Ticker(symbole).history(period="5d", interval="1d").dropna(subset=["Close"])
        if hist.empty:
            return f"Données indisponibles pour '{symbole}'."
        cours = float(hist.iloc[-1]["Close"])
        precedent = float(hist.iloc[-2]["Close"]) if len(hist) >= 2 else cours
        valeur = cours * qty
        valeur_prec = precedent * qty
        var = valeur - valeur_prec
        var_pct = (var / valeur_prec * 100) if valeur_prec else 0.0
        total += valeur
        total_precedent += valeur_prec
        resultats.append((symbole, qty, cours, valeur, var, var_pct))

    var_totale = total - total_precedent
    var_totale_pct = (var_totale / total_precedent * 100) if total_precedent else 0.0

    lignes_txt = ["Analyse du portefeuille :"]
    for symbole, qty, cours, valeur, var, var_pct in resultats:
        tendance = "📈" if var >= 0 else "📉"
        lignes_txt.append(
            f"- {symbole} x {qty:g} | Cours: {cours:.2f} $ | Valeur: {valeur:,.2f} $ | {tendance} {var:+,.2f} $ ({var_pct:+.2f}%)"
        )

    tendance_total = "📈" if var_totale >= 0 else "📉"
    lignes_txt.append(f"Valeur totale : {total:,.2f} $")
    lignes_txt.append(f"Variation globale : {tendance_total} {var_totale:+,.2f} $ ({var_totale_pct:+.2f}%)")

    return "\n".join(lignes_txt)
