from pyspark.sql import SparkSession    # type: ignore
from pyspark.sql.functions import from_json, col, from_unixtime, date_format, when, udf    # type: ignore
from pyspark.sql.types import StructType, StringType, LongType, BooleanType, IntegerType    # type: ignore
import requests    # type: ignore

spark = SparkSession.builder \
    .appName("BybitKafkaToElasticsearch") \
    .master("spark://spark-master:7077") \
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,"
            "org.elasticsearch:elasticsearch-spark-30_2.12:8.11.1") \
    .config("spark.es.nodes", "elasticsearch") \
    .config("spark.es.port", "9200") \
    .config("spark.es.nodes.wan.only", "true") \
    .config("spark.sql.caseSensitive", "true") \
    .getOrCreate()

# Schema dei messaggi Kafka
schema = StructType() \
    .add("i", StringType()) \
    .add("T", LongType()) \
    .add("p", StringType()) \
    .add("v", StringType()) \
    .add("S", StringType()) \
    .add("s", StringType()) \
    .add("BT", BooleanType()) \
    .add("RPI", BooleanType())

# Lettura da Kafka
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "bybit-trades") \
    .option("startingOffsets", "latest") \
    .load()

json_df = kafka_df.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select(
         col("data.i").alias("trade_id"),
         col("data.T").alias("original_time"),
         col("data.p").cast("double").alias("price"),
         col("data.v").cast("double").alias("quantity"),
         col("data.s").alias("symbol"),
         col("data.S").alias("side"),
         col("data.BT").alias("is_block_trade"),
         col("data.RPI").alias("reduce_position_indicator")
    )

df_converted = json_df.withColumn(
    "timestamp",
    date_format(
        from_unixtime(col("original_time") / 1000),
        "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
    )
).drop("original_time")

# Crea colonna is_buy
df_converted = df_converted.withColumn("is_buy", when(col("side") == "Buy", 1.0).otherwise(0.0))

# UDF per invocare il microservizio ML
def get_prediction(price, quantity, is_buy):
    """
    Invia una richiesta al servizio di Machine Learning per ottenere una predizione 
    basata su prezzo, quantità e direzione dell'operazione (acquisto o vendita).

    Parametri:
    - price (float): Il prezzo dell'operazione.
    - quantity (float): La quantità dell'operazione.
    - is_buy (bool): True se l'operazione è un acquisto, False se è una vendita.

    Ritorna:
    - int: La predizione restituita dal modello ML (es. 1 o 0). 
           In caso di errore nella richiesta, restituisce 0.
    """
    try:
        payload = {
            "price": price,
            "quantity": quantity,
            "is_buy": is_buy
        }
        response = requests.post("http://ml-service:8000/predict", json=payload, timeout=1)
        result = response.json()
        return int(result.get("prediction", 0))
    except Exception:
        return 0

# Registra la UDF
prediction_udf = udf(get_prediction, IntegerType())

# Applica la predizione
df_enriched = df_converted.withColumn("prediction", prediction_udf("price", "quantity", "is_buy"))

# Scrive su Elasticsearch
query = df_enriched.writeStream \
    .format("es") \
    .option("checkpointLocation", "/tmp/spark-checkpoint") \
    .option("es.resource", "bybit-trades") \
    .option("es.index.auto.create", "true") \
    .start()

query.awaitTermination()
