import requests  # type: ignore

def get_usdt_symbols(limit=100):
    """
    Recupera un elenco dei simboli di criptovalute scambiati contro USDT nel mercato spot
    dalla API di Bybit, ordinati per volume di scambio nelle ultime 24 ore.

    Parametri:
    - limit (int): Numero massimo di simboli da restituire (default: 100)

    Ritorna:
    - list[str]: Lista dei simboli (es. ["BTCUSDT", "ETHUSDT", ...]).
                 Restituisce una lista vuota in caso di errore nella richiesta.
    """
    url = "https://api.bybit.com/v5/market/instruments-info"
    params = {"category": "spot"}

    response = requests.get(url, params=params)
    data = response.json()

    if data["retCode"] != 0:
        print("Error in retrieving symbols:", data["retMsg"])
        return []

    symbols = sorted(
        (item for item in data["result"]["list"]
         if item["quoteCoin"] == "USDT" and item["status"] == "Trading"),
        key=lambda x: float(x.get("volume24h", 0)),
        reverse=True
    )

    return [item["symbol"] for item in symbols[:limit]]
