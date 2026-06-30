"""
upload_referentiel.py
---------------------
Upload du referentiel Anfa dans MinIO (bucket anfa-raw/referentiel/).
A executer depuis le conteneur spark-master :

  docker exec -e HOME=/tmp anfa-spark-master python3 /opt/jobs/upload_referentiel.py
"""
import boto3
from pathlib import Path

MINIO_ENDPOINT = "http://minio:9000"
ACCESS_KEY     = "anfa-app-key"
SECRET_KEY     = "anfa-app-secret-2026"
BUCKET         = "anfa-raw"
DATA_DIR       = Path("/opt/data/referentiel")
FILES          = ["arrets.csv", "bus.csv", "lignes.csv", "tarifs.csv"]


def get_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    )


def ensure_bucket(client, bucket):
    try:
        client.head_bucket(Bucket=bucket)
    except Exception:
        client.create_bucket(Bucket=bucket)
        print(f"[OK] Bucket '{bucket}' cree.")


def main():
    client = get_client()
    ensure_bucket(client, BUCKET)
    ensure_bucket(client, "anfa-processed")

    for filename in FILES:
        local_path = DATA_DIR / filename
        s3_key     = f"referentiel/{filename}"

        if not local_path.exists():
            print(f"[WARN] Fichier introuvable : {local_path}")
            continue

        client.upload_file(str(local_path), BUCKET, s3_key)
        print(f"[OK] {filename} -> s3://{BUCKET}/{s3_key}")

    print("\nVerification dans la console MinIO : http://localhost:9001")
    print(f"  Bucket : {BUCKET}/referentiel/ doit contenir {len(FILES)} CSV.")


if __name__ == "__main__":
    main()
