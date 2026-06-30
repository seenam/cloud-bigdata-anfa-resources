"""
generer_trajets.py
-------------------
Genere un historique simule de trajets (30 jours) et le depose
directement dans MinIO : anfa-raw/trajets/trajets_30j.csv

Distribution realiste des heures de pointe (poids plus forts vers 7-8h et 17-18h).

Executer :
  docker exec -e HOME=/tmp anfa-spark-master python3 /opt/jobs/generer_trajets.py
"""
import csv
import io
import random
import boto3
from datetime import date, datetime, timedelta

MINIO_ENDPOINT = "http://minio:9000"
ACCESS_KEY     = "anfa-app-key"
SECRET_KEY     = "anfa-app-secret-2026"
BUCKET         = "anfa-raw"
S3_KEY         = "trajets/trajets_30j.csv"

LIGNES   = [f"L{i:02d}" for i in range(1, 13)]
NB_JOURS = 30

# Plus le poids est eleve, plus l'heure est frequente (pics matin/soir)
HEURES_POIDS = {
    5: 1,  6: 5,  7: 15, 8: 18, 9: 10, 10: 6, 11: 5, 12: 7,
    13: 6, 14: 5, 15: 5, 16: 8, 17: 17, 18: 18, 19: 12,
    20: 6, 21: 3, 22: 1,
}


def get_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )


def generer_trajets():
    random.seed(42)
    heures = list(HEURES_POIDS.keys())
    poids  = list(HEURES_POIDS.values())

    trajets = []
    debut = date.today() - timedelta(days=NB_JOURS)

    for j in range(NB_JOURS):
        jour = debut + timedelta(days=j)
        for ligne in LIGNES:
            nb = random.randint(18, 32)   # ~25 trajets/ligne/jour
            heures_tirees = random.choices(heures, weights=poids, k=nb)
            for h in heures_tirees:
                minute  = random.randint(0, 59)
                seconde = random.randint(0, 59)
                depart  = datetime(jour.year, jour.month, jour.day, h, minute, seconde)
                duree   = random.randint(15, 90)
                arrivee = depart + timedelta(minutes=duree)
                # retard : distribution gaussienne centrée sur 2 min, ecart-type 5
                retard  = max(0.0, round(random.gauss(2, 5), 1))
                trajets.append({
                    "trajet_id":    f"{ligne}-{jour.strftime('%Y%m%d')}-{h:02d}{minute:02d}",
                    "ligne_id":     ligne,
                    "depart":       depart.isoformat(),
                    "arrivee":      arrivee.isoformat(),
                    "passagers":    random.randint(5, 85),
                    "retard_min":   retard,
                    "jour_semaine": jour.weekday(),  # 0=lundi ... 6=dimanche
                })
    return trajets


def main():
    print("Generation de l'historique simule (30 jours x 12 lignes)...")
    trajets = generer_trajets()

    # Serialiser en CSV en memoire (evite d'ecrire sur le disque local)
    output     = io.StringIO()
    fieldnames = ["trajet_id","ligne_id","depart","arrivee","passagers","retard_min","jour_semaine"]
    writer     = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(trajets)
    content = output.getvalue().encode("utf-8")

    # Upload dans MinIO
    client = get_client()
    client.put_object(
        Bucket=BUCKET,
        Key=S3_KEY,
        Body=content,
        ContentType="text/csv",
    )
    print(f"[OK] ~{len(trajets):,} trajets generes -> s3://{BUCKET}/{S3_KEY}")
    print("Verifiez dans la console MinIO : http://localhost:9001")


if __name__ == "__main__":
    main()
