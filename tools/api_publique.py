import requests

API_BASE_URL = "https://api.frankfurter.app"

def convertir_devise(input_str: str) -> str:
    parties = input_str.strip().split(',')
    montant = float(parties[0])
    devise_from = parties[1].strip().upper()
    devise_to = parties[2].strip().upper()
    response = requests.get(f"{API_BASE_URL}/latest", params={"amount": montant, "from": devise_from, "to": devise_to}, timeout=5)
    if response.status_code != 200:
        return f"Erreur API : {response.status_code}"
    data = response.json()
    montant_converti = data["rates"][devise_to]
    taux = montant_converti / montant
    return (f"{montant:.2f} {devise_from} = {montant_converti:.2f} {devise_to}\n"
            f"Taux : 1 {devise_from} = {taux:.4f} {devise_to}")

def obtenir_taux_du_jour(devise_base: str = "EUR") -> str:
    devise_base = devise_base.strip().upper()
    response = requests.get(f"{API_BASE_URL}/latest", params={"from": devise_base}, timeout=5)
    if response.status_code != 200:
        return f"Erreur API : {response.status_code}"
    data = response.json()
    devises_cles = ["USD", "GBP", "JPY", "CHF", "CAD", "AUD", "CNY"]
    result = f"Taux du jour ({data['date']}) — Base : {devise_base}\n"
    for dev in devises_cles:
        if dev in data["rates"] and dev != devise_base:
            result += f"  1 {devise_base} = {data['rates'][dev]:.4f} {dev}\n"
    return result
