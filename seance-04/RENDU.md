# Rendu — Séance 4

**Nom et prénom :** KUMAKO [Votre nom complet]  
**Identifiant GitHub :** [votre-username]  
**Date de soumission :** 27/06/2025

## Résumé de la séance

Terraform a été installé et configuré sur la machine locale. Une infrastructure Docker complète (réseau, volume, conteneur MinIO) a été décrite en HCL (HashiCorp Configuration Language). Le workflow fondamental `init` → `plan` → `apply` → `destroy` a été maîtrisé, ainsi que le rôle du state Terraform et ses bonnes pratiques de versioning. Le code a ensuite été refactorisé avec des variables et un fichier `.tfvars` pour le rendre propre et réutilisable.

## Étapes principales

1. Installation de Terraform et premier `main.tf` minimal.
2. Maîtrise du workflow `init` → `plan` → `apply` → `destroy`.
3. Compréhension du state Terraform et bonnes pratiques de versioning.
4. Stack complète : réseau, volume, conteneur MinIO.
5. Refactoring en variables et fichier `.tfvars`.

## Captures d'écran

### terraform plan (création initiale)
![terraform plan](captures/terraform-plan.png)

### terraform apply réussi
![terraform apply](captures/terraform-apply.png)

### Console MinIO créée par Terraform
![Console MinIO](captures/console-minio-tf.png)

### terraform destroy
![terraform destroy](captures/terraform-destroy.png)

## Réponses aux exercices d'application

_À compléter d'après les énoncés fournis avec l'assignment._

**Q1 – Que contient le fichier `terraform.tfstate` et pourquoi ne doit-on jamais le committer ?**  
Le fichier `terraform.tfstate` contient l'état complet de l'infrastructure gérée par Terraform : les IDs des ressources, leurs configurations, et les valeurs des variables y compris les secrets (mots de passe) en clair. On ne doit jamais le committer car il exposerait des secrets sur GitHub, et Terraform en a besoin dans son état exact pour détecter les dérives.

**Q2 – Qu'est-ce que l'idempotence dans le contexte Terraform ?**  
L'idempotence signifie qu'appliquer plusieurs fois la même configuration produit toujours le même résultat. Si l'infrastructure correspond déjà au code, `terraform apply` répond `No changes` sans rien modifier.

**Q3 – Quelle est la différence entre `+`, `-` et `~` dans un `terraform plan` ?**  
- `+` : création d'une nouvelle ressource  
- `-` : suppression d'une ressource existante  
- `~` : modification en place d'une ressource existante

## Difficultés rencontrées

_Aucune difficulté majeure rencontrée. Les pièges documentés dans le TP (ports déjà alloués, log_opts, tfstate dans Git) ont été anticipés grâce au guide fourni._
