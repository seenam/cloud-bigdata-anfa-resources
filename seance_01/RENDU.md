# Exercices d'application — Séance 1

**Étudiant :** KUMAKO Seenam Kodjo  
**Formation :** ESGIS Master 1 IA / Big Data  
**Module :** Cloud & Big Data

---

## Exercice 1 : QCM conceptuel

### 1.1
**Réponse : D. Open source obligatoire**  
Le NIST définit 5 caractéristiques essentielles du cloud (élasticité rapide, service mesuré, mutualisation des ressources, libre-service à la demande, accès réseau large bande) — l'open source n'en fait pas partie.

### 1.2
**Réponse : C. SaaS**  
Gmail est une application complète accessible via navigateur ; l'utilisateur ne gère ni infrastructure, ni plateforme, ni code.

### 1.3
**Réponse : D. FaaS**  
FaaS (Function as a Service) est conçu pour exécuter des fonctions courtes déclenchées par des événements, sans serveur dédié tournant en permanence.

### 1.4
**Réponse : C. Cloud hybride**  
Le cloud hybride permet de conserver les données sensibles sur un cloud privé/on-premise tout en profitant de l'élasticité du cloud public pour les analyses non sensibles.

### 1.5
**Réponse : B. La situation où une entreprise ne peut plus changer de fournisseur sans coûts ou risques majeurs**  
Le vendor lock-in désigne la dépendance technologique ou contractuelle qui rend le changement de fournisseur difficile et coûteux.

### 1.6
**Réponse : C. Un service open source est forcément moins performant qu'un service managé propriétaire**  
C'est faux : des outils open source comme Spark, Kafka ou MinIO sont utilisés en production à très grande échelle et rivalisent avec les services propriétaires.

---

## Exercice 2 : Classification de services

| Service | Modèle | Justification |
|---|---|---|
| Google Compute Engine | IaaS | Fournit des machines virtuelles brutes ; l'utilisateur gère l'OS et tout ce qui est au-dessus. |
| AWS Lambda | FaaS | Exécute des fonctions à la demande, déclenchées par des événements, sans gestion de serveur. |
| Snowflake | SaaS | Entrepôt de données entièrement managé, accessible via interface web sans gestion d'infrastructure. |
| Heroku | PaaS | Plateforme de déploiement d'applications ; l'utilisateur pousse son code et Heroku gère le reste. |
| Microsoft 365 | SaaS | Applications bureautiques complètes consommées via navigateur, sans installation ni gestion. |
| Databricks | PaaS | Plateforme Spark managée ; l'utilisateur écrit ses jobs, Databricks gère les clusters. |
| Azure Functions | FaaS | Fonctions déclenchées par événements sur Azure, sans serveur dédié. |
| Tableau Online | SaaS | Outil de visualisation entièrement hébergé et managé, accessible via navigateur. |

---

## Exercice 3 : Lecture et interprétation

### 3.1 — Commande `docker run`

```
docker run -d --name analyse-anfa -p 8888:8888 -v /home/koffi/notebooks:/notebooks \
  -e JUPYTER_TOKEN=anfa-token \
  jupyter/pyspark-notebook
```

| Option | Signification |
|---|---|
| `-d` | Lance le conteneur en arrière-plan (detached), sans bloquer le terminal. |
| `--name analyse-anfa` | Donne le nom `analyse-anfa` au conteneur. |
| `-p 8888:8888` | Redirige le port 8888 de l'hôte vers le port 8888 du conteneur (accès Jupyter). |
| `-v /home/koffi/notebooks:/notebooks` | Monte le dossier local `/home/koffi/notebooks` dans le conteneur à `/notebooks` pour persister les notebooks. |
| `-e JUPYTER_TOKEN=anfa-token` | Définit la variable d'environnement `JUPYTER_TOKEN` pour sécuriser l'accès à Jupyter. |
| `jupyter/pyspark-notebook` | Image Docker utilisée, contenant Jupyter avec PySpark préinstallé. |

**Ce que fait la commande entière :** Cette commande lance un serveur Jupyter avec PySpark dans un conteneur Docker, accessible depuis le navigateur à `http://localhost:8888` avec le token `anfa-token`. Les notebooks créés sont sauvegardés sur le disque local de la machine hôte grâce au volume monté.

---

### 3.2 — Lecture du `docker-compose.yml`

**a. URLs accessibles depuis le navigateur de l'hôte :**
- `http://localhost:9000` → API S3 (accès programmatique)
- `http://localhost:9001` → Console web d'administration MinIO

**b. Suppression et relance du conteneur :**  
Les données **ne sont pas perdues**. Le volume `minio-data` est indépendant du conteneur — il persiste sur le disque de l'hôte. En relançant `docker compose up -d`, MinIO retrouve ses données intactes car le volume est remonté automatiquement.

**c. Problème de sécurité en production :**  
Le mot de passe `secret` est écrit en clair dans le fichier `docker-compose.yml`. En production, il faudrait utiliser des **secrets Docker** ou un fichier `.env` exclu du dépôt Git pour ne jamais exposer les credentials dans le code source.

---

## Exercice 4 : Diagnostic

**a. Cause précise de l'erreur :**  
L'étudiant utilise `aws_access_key_id="anfa-admin"` et `aws_secret_access_key="anfa-password-2026"` qui sont les **identifiants root** de MinIO. Or l'API S3 de MinIO n'accepte que les **clés applicatives** (service accounts) créées via `mc` — il a bien créé `anfa-app-key` / `anfa-app-secret-2026` mais ne les utilise pas dans son script.

**b. Correction du code :**

```python
s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id="anfa-app-key",           # ← clé applicative
    aws_secret_access_key="anfa-app-secret-2026",  # ← secret applicatif
    region_name="us-east-1",
)
```

**c. Pourquoi MinIO refuse les identifiants root via l'API S3 :**  
La console web (port 9001) utilise son propre système d'authentification HTTP qui accepte les identifiants root. En revanche, l'API S3 (port 9000) ne reconnaît que les **clés applicatives** (service accounts) créées via `mc` — les identifiants root ne sont pas des clés S3 valides pour les appels programmatiques.

---

## Exercice 5 : Mini-cas d'architecture

### a. Deux limites de l'architecture actuelle

1. **Absence de temps réel :** Un export CSV mensuel ne permet pas des prédictions horaires — les données sont trop anciennes pour répondre aux besoins opérationnels.
2. **Absence de scalabilité :** Le PC du data scientist a des ressources fixes ; il ne peut pas absorber les pics de calcul (vendredi soir, fêtes) et bloque si plusieurs analystes veulent travailler simultanément.

### b. Caractéristiques NIST par besoin

| Besoin | Caractéristique NIST | Explication |
|---|---|---|
| Prédictions horaires | Service mesuré | On paie uniquement le calcul consommé chaque heure, sans ressource idle entre les exécutions. |
| Tableau de bord partagé | Accès réseau large bande | Le cloud rend le tableau de bord accessible depuis n'importe quel navigateur sans installation locale. |
| Élasticité lors des pics | Élasticité rapide | Les ressources de calcul s'ajustent automatiquement selon la charge, sans intervention manuelle. |
| Maîtriser les coûts | Service mesuré | Le pay-as-you-go évite de sur-provisionner des serveurs fixes coûteux à l'année. |
| Données dans un environnement contrôlé | Mutualisation des ressources | Un cloud privé dédié permet d'isoler les données clients des autres tenants. |

### c. Modèles de service par composant

- **(i) Tableau de bord partagé → SaaS :** Un outil comme Tableau Online ou Looker est consommé directement via navigateur, sans gestion d'infrastructure ni de code.
- **(ii) Calcul des prédictions à l'heure → FaaS :** Une fonction déclenchée toutes les heures pour recalculer les prédictions est idéale pour FaaS (AWS Lambda, Azure Functions) — pas de serveur idle entre les exécutions.
- **(iii) Stockage des données clients → IaaS :** Pour respecter la conformité, le stockage est hébergé sur une infrastructure dédiée et contrôlée (cloud privé ou IaaS avec zone géographique maîtrisée).

### d. Modèle de déploiement recommandé : Cloud hybride

Les données clients sensibles restent sur un cloud privé ou on-premise pour respecter les contraintes de conformité réglementaire. En parallèle, les workloads de calcul (entraînement des modèles, tableaux de bord) s'appuient sur le cloud public pour bénéficier de l'élasticité lors des pics. Ce modèle hybride offre le meilleur compromis entre conformité, maîtrise des coûts et performance.

### e. Trois stratégies contre le vendor lock-in

1. **Utiliser des outils open source** (MinIO, Spark, Kafka) compatibles avec plusieurs clouds — le code fonctionne à l'identique sur AWS, GCP ou Azure.
2. **Adopter des standards ouverts** comme l'API S3 pour le stockage objet — changer de fournisseur ne nécessite que de modifier l'URL et les credentials.
3. **Conteneuriser les applications** avec Docker/Kubernetes — les conteneurs sont portables d'un cloud à l'autre sans réécriture du code.
