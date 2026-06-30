"""
analyse_referentiel_cluster.py
-------------------------------
Job PySpark distribue — Analyse du referentiel Anfa.

Differences vs seance 2 (local) :
  1. master("spark://spark-master:7077") au lieu de master("local[*]")
  2. Lecture via s3a://anfa-raw/...  au lieu de /data/referentiel/...
  3. Configuration S3A pour parler a MinIO

Soumettre avec spark-submit :
  docker exec -e HOME=/tmp anfa-spark-master /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --conf spark.jars.ivy=/tmp/.ivy2 \
    --packages "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262" \
    /opt/jobs/analyse_referentiel_cluster.py
"""
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as spark_sum


def create_spark_session():
    return (
        SparkSession.builder
        .appName("Anfa - Analyse referentiel (cluster)")
        .master("spark://spark-master:7077")
        # ── Connecteur S3A vers MinIO ───────────────────────────────
        .config("spark.hadoop.fs.s3a.endpoint",              "http://minio:9000")
        .config("spark.hadoop.fs.s3a.access.key",            "anfa-app-key")
        .config("spark.hadoop.fs.s3a.secret.key",            "anfa-app-secret-2026")
        .config("spark.hadoop.fs.s3a.path.style.access",     "true")
        .config("spark.hadoop.fs.s3a.impl",                  "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled","false")
        # ── Packages Maven (telecharges au premier lancement) ───────
        .config("spark.jars.packages",
                "org.apache.hadoop:hadoop-aws:3.3.4,"
                "com.amazonaws:aws-java-sdk-bundle:1.12.262")
        .getOrCreate()
    )


def main():
    t0    = time.time()
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    print("=" * 60)
    print("  ANALYSE DU REFERENTIEL ANFA  CLUSTER")
    print("=" * 60)

    # ── Lecture des 4 CSV depuis MinIO ─────────────────────────────
    BASE = "s3a://anfa-raw/referentiel"
    lignes = spark.read.csv(f"{BASE}/lignes.csv", header=True, inferSchema=True)
    arrets = spark.read.csv(f"{BASE}/arrets.csv", header=True, inferSchema=True)
    bus    = spark.read.csv(f"{BASE}/bus.csv",    header=True, inferSchema=True)
    tarifs = spark.read.csv(f"{BASE}/tarifs.csv", header=True, inferSchema=True)

    # ── Statistiques globales ───────────────────────────────────────
    nb_lignes       = lignes.count()
    nb_arrets       = arrets.select("arret_id").distinct().count()
    nb_bus          = bus.count()
    nb_actifs       = bus.filter(col("actif") == True).count()
    capacite_totale = bus.agg(spark_sum("capacite").alias("t")).collect()[0]["t"]

    print(f"\nNombre de lignes          : {nb_lignes}")
    print(f"Nombre d'arrets uniques   : {nb_arrets}")
    print(f"Nombre total de bus       : {nb_bus}")
    print(f"Dont actifs               : {nb_actifs}")
    print(f"Capacite totale flotte    : {capacite_totale} places")

    # ── Repartition des bus actifs par ligne ────────────────────────
    print("\nRepartition des bus actifs par ligne :")
    bus_par_ligne = (
        bus.filter(col("actif") == True)
        .groupBy("ligne_assignee")
        .agg(
            count("*").alias("nb_bus"),
            spark_sum("capacite").alias("capacite_totale"),
        )
        .orderBy(col("nb_bus").desc())
    )
    bus_par_ligne.show(20, truncate=False)

    # ── Ecriture en Parquet dans anfa-processed ─────────────────────
    OUTPUT = "s3a://anfa-processed/bus_par_ligne"
    print(f"Ecriture des resultats dans {OUTPUT}...")
    bus_par_ligne.write.mode("overwrite").parquet(OUTPUT)
    print("[OK] Resultats ecrits en Parquet.")

    elapsed = time.time() - t0
    print(f"\nAnalyse terminee en {elapsed:.1f}s.")
    spark.stop()


if __name__ == "__main__":
    main()
