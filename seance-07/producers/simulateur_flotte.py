"""
simulateur_flotte.py

Simule une flotte de 100 bus Anfa envoyant leur position GPS en continu
sur le topic anfa-positions-bus, a raison d'une vague de ~100
positions/seconde.

Chaque message est publie avec key=bus_id : cela garantit que toutes les
positions d'un meme bus arrivent dans l'ordre, dans la meme partition
(exactement le principe vu en CM).

Laissez ce script tourner dans un terminal dedie pendant que vous
explorez Kafka UI, testez la tolerance aux pannes (Partie 5) et lancez
les jobs Spark Streaming (Partie 6) dans d'autres terminaux.
"""
import json
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer

TOPIC = "anfa-positions-bus"
NB_BUS = 100
NB_LIGNES = 10

# Zone geographique de reference pour generer des coordonnees plausibles
LAT_BASE = 6.13
LON_BASE = 1.22

producer = KafkaProducer(
    bootstrap_servers=["localhost:19092", "localhost:19093", "localhost:19094"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8") if k else None,
)


def construire_flotte():
    flotte = []
    for i in range(1, NB_BUS + 1):
        flotte.append(
            {
                "bus_id": f"B{i:03d}",
                "ligne_id": f"L{random.randint(1, NB_LIGNES):02d}",
                "latitude": LAT_BASE + random.uniform(-0.05, 0.05),
                "longitude": LON_BASE + random.uniform(-0.05, 0.05),
            }
        )
    return flotte


def main():
    flotte = construire_flotte()
    print(f"[INFO] Flotte simulee : {len(flotte)} bus sur {NB_LIGNES} lignes.")
    print("[INFO] Envoi en continu sur le topic 'anfa-positions-bus' (Ctrl+C pour arreter).")

    vague = 0
    try:
        while True:
            timestamp = datetime.now(timezone.utc).isoformat()
            for bus in flotte:
                # Deplacement aleatoire leger pour simuler le mouvement du bus
                bus["latitude"] += random.uniform(-0.0005, 0.0005)
                bus["longitude"] += random.uniform(-0.0005, 0.0005)

                message = {
                    "bus_id": bus["bus_id"],
                    "ligne_id": bus["ligne_id"],
                    "latitude": round(bus["latitude"], 6),
                    "longitude": round(bus["longitude"], 6),
                    "vitesse_kmh": random.randint(0, 60),
                    "timestamp": timestamp,
                }

                # La cle = bus_id : garantit l'ordre des positions PAR bus
                producer.send(TOPIC, key=bus["bus_id"], value=message)

            producer.flush()
            vague += 1
            print(f"[VAGUE {vague}] {len(flotte)} positions envoyees a {timestamp}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Simulateur arrete.")


if __name__ == "__main__":
    main()
