FROM python:3.13.3

WORKDIR /app

COPY bybit_to_kafka.py .

COPY bybit_symbols.py .

RUN pip install kafka-python requests websocket-client

CMD ["python", "bybit_to_kafka.py"]
