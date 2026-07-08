# Rendu — Séance 10

**Nom et prénom :** <Votre nom complet>
**Identifiant GitHub :** <votre-username>
**Date de soumission :** <JJ/MM/AAAA>

## Résumé de la séance

<2-4 lignes : serveur MLflow déployé, 3 runs d'entraînement tracés et comparés,
meilleur modèle enregistré en Production dans le Registry, fiche de conformité rédigée.>

## Étapes principales

1. Déploiement d'un serveur MLflow Tracking (SQLite + stockage local).
2. Génération d'un jeu de données d'affluence Anfa et entraînement de 3 variantes
   d'un modèle RandomForest, chacune tracée avec MLflow.
3. Comparaison des runs dans l'UI et identification du meilleur candidat.
4. Enregistrement du modèle dans le Model Registry, transition en statut Production.
5. Rédaction d'une fiche de conformité pour un scénario d'application mobile Anfa.

## Captures d'écran

### Tableau des 3 runs comparés
![Runs MLflow](captures/mlflow-runs.png)

### Modèle enregistré en statut Production
![Registry Production](captures/mlflow-registry-production.png)

## Réflexion personnelle

<3-5 lignes : en quoi le Model Registry résout-il le problème de Kossi dans la
situation-problème du CM ? Quel est le lien entre "versionner un modèle" (aujourd'hui)
et "versionner une infrastructure" (Terraform, séance 4) ?>

## Difficultés rencontrées

<Aucune | Décrivez brièvement.>
