from pyspark.sql import SparkSession
from pyspark.sql.functions import sum as spark_sum, count, avg, desc, col

DATA_DIR = "/data/referentiel"  # chemin DANS le conteneur (bind mount)


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("Anfa - Analyse du référentiel")
        .master("local[*]")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    # ── Lecture des 4 CSV ──────────────────────────────────────────
    lignes = spark.read.csv(f"{DATA_DIR}/lignes.csv",  header=True, inferSchema=True)
    arrets = spark.read.csv(f"{DATA_DIR}/arrets.csv",  header=True, inferSchema=True)
    bus    = spark.read.csv(f"{DATA_DIR}/bus.csv",     header=True, inferSchema=True)
    tarifs = spark.read.csv(f"{DATA_DIR}/tarifs.csv",  header=True, inferSchema=True)

    print("\n" + "=" * 60)
    print("   ANALYSE DU RÉFÉRENTIEL ANFA")
    print("=" * 60)

    # ── 1. Statistiques générales ──────────────────────────────────
    nb_lignes  = lignes.count()
    nb_arrets  = arrets.select("id_arret").distinct().count()
    nb_bus     = bus.count()
    nb_actifs  = bus.filter(col("statut") == "actif").count()
    capacite   = bus.agg(spark_sum("capacite").alias("total")).collect()[0]["total"]

    print(f"\n Nombre de lignes de bus     : {nb_lignes}")
    print(f" Nombre d'arrêts uniques     : {nb_arrets}")
    print(f" Nombre total de bus         : {nb_bus}")
    print(f"   Dont actifs              : {nb_actifs}")
    print(f" Capacité totale de la flotte: ~{int(capacite)} places")

    # ── 2. Top 3 des lignes les plus longues ───────────────────────
    print("\n Top 3 des lignes les plus longues :")
    top3 = (
        lignes
        .orderBy(desc("distance_km"))
        .limit(3)
        .select("nom", "distance_km")
        .collect()
    )
    for i, row in enumerate(top3, 1):
        print(f"   {i}. {row['nom']:<35} {row['distance_km']:.2f} km")

    # ── 3. Tarif moyen par type ────────────────────────────────────
    print("\n Tarif moyen par type :")
    tarifs.groupBy("type") \
          .agg(avg("prix_fcfa").alias("prix_moyen")) \
          .orderBy("type") \
          .show(truncate=False)

    # ── 4. Nombre d'arrêts par ligne ──────────────────────────────
    print("\n Nombre d'arrêts par ligne :")
    lignes.select("nom", "nb_arrets") \
          .orderBy(desc("nb_arrets")) \
          .show(5, truncate=False)

    print("=" * 60)
    print("   Analyse terminée.")
    print("=" * 60 + "\n")

    spark.stop()


if __name__ == "__main__":
    main()
