"""
premier_producer.py

Producer Kafka minimal pour comprendre le fonctionnement de base : envoie
5 messages de test sur le topic anfa-positions-bus, tous avec la meme cle
("B001"), afin d'observer dans Kafka UI qu'ils atterrissent tous dans la
meme partition (garantie d'ordre par cle).

Ce script tourne sur la machine hote (pas dans un conteneur Docker) : on
se connecte donc via les ports EXTERNES exposes par le docker-compose
(19092, 19093, 19094), pas le port interne (9092) utilise entre conteneurs.
"""
import json
import time

from kafka import KafkaProducer

TOPIC = "anfa-positions-bus"

producer = KafkaProducer(
    bootstrap_servers=["localhost:19092", "localhost:19093", "localhost:19094"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8") if k else None,
)


def main():
    for i in range(5):
        message = {
            "bus_id": "B001",
            "message_numero": i,
            "contenu": f"Message de test numero {i}",
        }
        # send() est ASYNCHRONE ; la cle "B001" determine la partition de destination.
        producer.send(TOPIC, key="B001", value=message)
        print(f"[ENVOYE] {message}")
        time.sleep(0.2)

    producer.flush()
    print("[OK] 5 messages envoyes.")


if __name__ == "__main__":
    main()
