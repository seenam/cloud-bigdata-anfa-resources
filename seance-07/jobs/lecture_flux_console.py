"""
lecture_flux_console.py

Premier job Spark Structured Streaming : lit le flux Kafka brut
(topic anfa-positions-bus), parse le JSON, et affiche le resultat en
console par micro-batch. Sert a valider que le pipeline Kafka -> Spark
fonctionne avant de passer a l'agregation en fenetre
(voir agregation_streaming.py).

Soumission (depuis le conteneur anfa-spark-master) :

docker exec anfa-spark-master /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --conf spark.jars.ivy=/tmp/.ivy2 \
    --conf spark.driver.extraJavaOptions=-Duser.home=/tmp \
    --packages "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.8" \
    /opt/jobs/lecture_flux_console.py

Laissez tourner ~30 secondes puis arretez avec Ctrl+C.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType

KAFKA_BOOTSTRAP_SERVERS = "kafka-1:9092,kafka-2:9092,kafka-3:9092"
TOPIC = "anfa-positions-bus"

SCHEMA_POSITION = StructType(
    [
        StructField("bus_id", StringType(), True),
        StructField("ligne_id", StringType(), True),
        StructField("latitude", DoubleType(), True),
        StructField("longitude", DoubleType(), True),
        StructField("vitesse_kmh", IntegerType(), True),
        StructField("timestamp", StringType(), True),
    ]
)


def main():
    spark = SparkSession.builder.appName("AnfaLectureFluxConsole").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    # readStream (pas read) : c'est la seule vraie difference avec le batch.
    flux_brut = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", TOPIC)
        .option("startingOffsets", "latest")  # ne lit que les nouveaux messages
        .load()
    )

    positions = flux_brut.select(
        from_json(col("value").cast("string"), SCHEMA_POSITION).alias("data")
    ).select("data.*")

    requete = (
        positions.writeStream.outputMode("append")
        .format("console")
        .option("truncate", "false")
        .trigger(processingTime="5 seconds")
        .start()
    )

    requete.awaitTermination()


if __name__ == "__main__":
    main()
