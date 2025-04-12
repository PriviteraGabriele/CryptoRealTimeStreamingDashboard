FROM python:3.13.3

WORKDIR /app

COPY kafka_consumer.py .

RUN pip install kafka-python

CMD ["python", "kafka_consumer.py"]