import websocket
import json
from kafka import KafkaProducer
import threading
import time
from bybit_symbols import get_usdt_symbols
import os

KAFKA_HOST = os.getenv("KAFKA_HOST", "kafka:29092")
producer = KafkaProducer(bootstrap_servers=[KAFKA_HOST])

symbols = get_usdt_symbols(limit=100)

def chunk_symbols(symbols, size=10):
    """
    Divide la lista dei simboli in sottoliste (batch) di dimensione specificata.

    Parametri:
    - symbols (list): Lista completa dei simboli.
    - size (int): Dimensione di ogni batch (default: 10).

    Ritorna:
    - generator: Batch di simboli da usare per ogni connessione WebSocket.
    """
    for i in range(0, len(symbols), size):
        yield symbols[i:i + size]

def create_ws_connection(batch_id, batch_symbols):
    """
    Crea una connessione WebSocket per ricevere in tempo reale i trade
    pubblici relativi ad un batch di simboli dal feed Bybit.

    Parametri:
    - batch_id (int): Identificativo del batch (per log).
    - batch_symbols (list): Lista dei simboli USDT da sottoscrivere nella connessione.

    La funzione:
    - Sottoscrive i canali WebSocket per i simboli specificati.
    - Invia i dati ricevuti su un topic Kafka chiamato 'bybit-trades'.
    """

    def on_message(ws, message):
        """
        Gestisce i messaggi ricevuti dal WebSocket.
        Filtra i messaggi in base ai simboli sottoscritti e li invia a Kafka.
        """
        data = json.loads(message)
        topic = data.get("topic", "")
        if any(topic.endswith(symbol) for symbol in batch_symbols):
            for trade in data.get("data", []):
                producer.send("bybit-trades", json.dumps(trade).encode("utf-8"))
                print(f"[Batch {batch_id}] Trade sent ({topic}):", trade)

    def on_error(ws, error):
        """
        Gestisce gli errori della connessione WebSocket.
        """
        print(f"[Batch {batch_id}] WebSocket error:", error)

    def on_close(ws, close_status_code, close_msg):
        """
        Gestisce la chiusura della connessione WebSocket.
        """
        print(f"[Batch {batch_id}] WebSocket closed")

    def on_open(ws):
        """
        Sottoscrive i canali dei trade pubblici per ogni simbolo del batch.
        """
        args = [f"publicTrade.{symbol}" for symbol in batch_symbols]
        payload = {"op": "subscribe", "args": args}
        ws.send(json.dumps(payload))
        print(f"[Batch {batch_id}] Subscribed to: {', '.join(batch_symbols)}")

    ws = websocket.WebSocketApp(
        "wss://stream.bybit.com/v5/public/spot",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

threads = []
for batch_id, symbol_batch in enumerate(chunk_symbols(symbols)):
    t = threading.Thread(target=create_ws_connection, args=(batch_id, symbol_batch))
    t.start()
    threads.append(t)
    time.sleep(1)

for t in threads:
    t.join()
