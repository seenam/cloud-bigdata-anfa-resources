"""
agregation_streaming.py

Deuxieme job Spark Structured Streaming : agrege le flux de positions GPS
en fenetres temporelles de 30 secondes (nombre de positions recues et
vitesse moyenne, par ligne), puis ecrit le resultat en Parquet dans MinIO
(s3a://anfa-streaming/agregats_par_ligne/).

Pre-requis MinIO (voir 6.2 du TP) : la cle applicative anfa-app-key doit
exister, et le bucket anfa-streaming doit etre cree.

Soumission (depuis le conteneur anfa-spark-master) :

docker exec anfa-spark-master /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --conf spark.jars.ivy=/tmp/.ivy2 \
    --conf spark.driver.extraJavaOptions=-Duser.home=/tmp \
    --packages "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.8,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262" \
    /opt/jobs/agregation_streaming.py

Laissez tourner 2 a 3 minutes (le temps d'accumuler plusieurs fenetres de
30 secondes), puis arretez avec Ctrl+C.
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col, count, from_json, window
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType

KAFKA_BOOTSTRAP_SERVERS = "kafka-1:9092,kafka-2:9092,kafka-3:9092"
TOPIC = "anfa-positions-bus"

MINIO_ENDPOINT = "http://minio:9000"
MINIO_ACCESS_KEY = "anfa-app-key"
MINIO_SECRET_KEY = "anfa-app-secret-2026"

OUTPUT_PATH = "s3a://anfa-streaming/agregats_par_ligne/"
CHECKPOINT_PATH = "s3a://anfa-streaming/checkpoints/agregats_par_ligne/"

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


def build_spark_session():
    return (
        SparkSession.builder.appName("AnfaAgregationStreaming")
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT)
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
        )
        .getOrCreate()
    )


def main():
    spark = build_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    flux_brut = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )

    positions = (
        flux_brut.select(
            from_json(col("value").cast("string"), SCHEMA_POSITION).alias("data")
        )
        .select("data.*")
        .withColumn("event_time", col("timestamp").cast("timestamp"))
    )

    agregats = (
        positions.withWatermark("event_time", "1 minute")  # tolere 1 min de retard
        .groupBy(
            window(col("event_time"), "30 seconds"),
            col("ligne_id"),
        )
        .agg(
            count("*").alias("nb_positions_recues"),
            avg("vitesse_kmh").alias("vitesse_moyenne"),
        )
    )

    requete = (
        agregats.writeStream
        .outputMode("append")  # chaque fenetre n'est ecrite qu'une fois close
        .format("parquet")
        .option("path", OUTPUT_PATH)
        .option("checkpointLocation", CHECKPOINT_PATH)
        .trigger(processingTime="30 seconds")
        .start()
    )

    requete.awaitTermination()


if __name__ == "__main__":
    main()
