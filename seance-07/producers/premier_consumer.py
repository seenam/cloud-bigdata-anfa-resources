"""
premier_consumer.py

Consumer Kafka minimal : lit les messages du topic anfa-positions-bus
depuis le debut (auto_offset_reset="earliest") avec le consumer group
"mon-premier-groupe".

Relancer ce script tel quel ne relira PAS les memes messages : Kafka a
memorise l'offset consomme par ce group_id. Pour rejouer le flux depuis
zero, changez group_id (nouveau groupe = repart de zero), ou
repositionnez manuellement les offsets.
"""
import json

from kafka import KafkaConsumer

TOPIC = "anfa-positions-bus"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=["localhost:19092", "localhost:19093", "localhost:19094"],
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",  # lire depuis le debut du topic
    group_id="mon-premier-groupe",  # identifiant du consumer group
    consumer_timeout_ms=5000,  # s'arrete si rien de nouveau apres 5s
)


def main():
    nb_messages = 0
    for record in consumer:
        nb_messages += 1
        print(
            f"[RECU] partition={record.partition} offset={record.offset} "
            f"key={record.key} value={record.value}"
        )

    if nb_messages == 0:
        print("Fin de la lecture : aucun nouveau message pour ce group_id.")
    else:
        print(f"[OK] {nb_messages} message(s) lu(s).")


if __name__ == "__main__":
    main()
