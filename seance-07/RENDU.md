# Rendu - Seance 7 : Streaming Kafka et Spark Structured Streaming pour Anfa

**Nom :**
**Identifiant GitHub :**
**Date :**

## Resume

Decrivez en quelques phrases ce que vous avez mis en place pendant cette
seance : le cluster Kafka a 3 brokers en mode KRaft, le topic
`anfa-positions-bus`, le producer/consumer de decouverte, le simulateur de
flotte (100 bus), la demonstration de tolerance aux pannes, et les deux
jobs Spark Structured Streaming (lecture console puis agregation en
fenetre ecrite dans MinIO).

## Reflexion personnelle

Qu'avez-vous compris de l'interet de la cle (`key=bus_id`) dans un topic
partitionne ? Qu'avez-vous observe lorsque vous avez tue puis redemarre un
broker Kafka ? En quoi le `checkpointLocation` de Spark Structured
Streaming joue-t-il un role comparable aux offsets Kafka ?

## Reponses aux exercices

1. Pourquoi le cluster a-t-il survecu a l'arret de `anfa-kafka-2` sans
   perte de message ni interruption du simulateur ? Quel role jouent
   `KAFKA_DEFAULT_REPLICATION_FACTOR` et `KAFKA_MIN_INSYNC_REPLICAS` dans
   cette tolerance aux pannes ?

2. Pourquoi le consumer `premier_consumer.py` ne relit-il pas les memes
   messages lorsqu'on le relance avec le meme `group_id` ? Que faudrait-il
   changer pour rejouer tout l'historique du topic ?

3. A quoi sert le `withWatermark` dans `agregation_streaming.py` ? Que se
   passerait-il si on l'omettait sur un flux qui tourne indefiniment ?

## Difficultes rencontrees

Decrivez les problemes rencontres (demarrage des brokers, ports
externes/internes, packages Spark manquants, droits MinIO, RAM Docker,
etc.) et comment vous les avez resolus.

## Captures d'ecran

Toutes les captures se trouvent dans `captures/` :

- `kafka-ui-brokers.png` : liste des 3 brokers actifs dans Kafka UI
  (point de verification 1).
- `kafka-ui-debit.png` : Kafka UI montrant le debit de messages en
  augmentation pendant que le simulateur tourne (point de verification 4).
- `kafka-ui-2-brokers.png` : Kafka UI montrant 2 brokers actifs sur 3
  apres l'arret volontaire de `anfa-kafka-2` (point de verification 5).
- `spark-streaming-console.png` : 2-3 micro-batchs affiches en console
  par `lecture_flux_console.py` (point de verification 6).
- `minio-agregats.png` : structure du dossier `agregats_par_ligne/` dans
  le bucket MinIO `anfa-streaming` (point de verification 6 final).
