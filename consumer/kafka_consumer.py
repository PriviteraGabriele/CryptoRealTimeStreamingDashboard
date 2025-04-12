from kafka import KafkaConsumer
import json
import os

KAFKA_HOST = os.getenv("KAFKA_HOST", "kafka:29092")

consumer = KafkaConsumer(
    'bybit-trades',
    bootstrap_servers=[KAFKA_HOST],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='test-consumer',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("Listening on 'bybit-trades'...")

for message in consumer:
    print("Trade received:", message.value)
