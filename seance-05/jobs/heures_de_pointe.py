"""
heures_de_pointe.py
--------------------
Job PySpark distribue — Calcul des heures de pointe par ligne.

Pipeline :
  1. Lire l'historique depuis s3a://anfa-raw/trajets/trajets_30j.csv
  2. Extraire l'heure depuis le timestamp de depart
  3. groupBy("ligne_id", "heure")  →  shuffle entre les workers
  4. Ecrire en Parquet partitionne par ligne_id dans anfa-processed

Soumettre :
  docker exec -e HOME=/tmp anfa-spark-master /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --conf spark.jars.ivy=/tmp/.ivy2 \
    --packages "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262" \
    /opt/jobs/heures_de_pointe.py
"""
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as spark_sum, avg, hour


def create_spark_session():
    return (
        SparkSession.builder
        .appName("Anfa - Heures de pointe (cluster)")
        .master("spark://spark-master:7077")
        .config("spark.hadoop.fs.s3a.endpoint",              "http://minio:9000")
        .config("spark.hadoop.fs.s3a.access.key",            "anfa-app-key")
        .config("spark.hadoop.fs.s3a.secret.key",            "anfa-app-secret-2026")
        .config("spark.hadoop.fs.s3a.path.style.access",     "true")
        .config("spark.hadoop.fs.s3a.impl",                  "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled","false")
        .config("spark.jars.packages",
                "org.apache.hadoop:hadoop-aws:3.3.4,"
                "com.amazonaws:aws-java-sdk-bundle:1.12.262")
        .getOrCreate()
    )


def main():
    t0    = time.time()
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    # ── 1. Lecture depuis MinIO ─────────────────────────────────────
    trajets = spark.read.csv(
        "s3a://anfa-raw/trajets/trajets_30j.csv",
        header=True,
        inferSchema=True,
    )

    nb_trajets = trajets.count()
    print(f"\nTrajets analyses : {nb_trajets:,}")

    # ── 2. Extraction de l'heure depuis le timestamp de depart ─────
    trajets_avec_heure = trajets.withColumn("heure", hour(col("depart")))

    # ── 3. Agregation par ligne et par heure (groupBy = shuffle) ───
    pointe = (
        trajets_avec_heure
        .groupBy("ligne_id", "heure")
        .agg(
            count("*").alias("nb_trajets"),
            spark_sum("passagers").alias("total_passagers"),
            avg("retard_min").alias("retard_moyen"),
        )
    )

    print("\nTop 10 des heures les plus chargees par ligne :")
    (
        pointe
        .orderBy(col("nb_trajets").desc())
        .limit(10)
        .show(truncate=False)
    )

    # ── 4. Ecriture partitionnee (sous-dossiers ligne_id=L01/, ...) ─
    OUTPUT = "s3a://anfa-processed/heures_de_pointe"
    print(f"\nEcriture partitionnee dans {OUTPUT}...")
    (
        pointe
        .write
        .mode("overwrite")
        .partitionBy("ligne_id")
        .parquet(OUTPUT)
    )

    elapsed = time.time() - t0
    print("[OK] Resultats ecrits en Parquet partitionne par ligne_id.")
    print(f"\nAnalyse terminee en {elapsed:.1f}s.")
    spark.stop()


if __name__ == "__main__":
    main()
