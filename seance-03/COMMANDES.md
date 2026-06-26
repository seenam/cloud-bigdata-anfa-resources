# Commandes Séance 3 — à exécuter dans l'ordre

## ─── Partie 0 : Branche ───
git checkout main
git pull
git checkout -b seance-03
mkdir -p seance-03/manifests
cd seance-03
# (copier les 3 fichiers YAML dans manifests/)

## ─── Partie 1 : Installer Kind et kubectl (Windows) ───
winget install Kubernetes.kind
winget install Kubernetes.kubectl
# Fermer/rouvrir le terminal après installation, puis vérifier :
kind version
kubectl version --client

## ─── Partie 2 : Créer le cluster ───
kind create cluster --name anfa --image kindest/node:v1.35.1
docker ps                       # voir le conteneur anfa-control-plane
kubectl cluster-info
kubectl get nodes               # doit afficher anfa-control-plane Ready

## ─── Partie 3 : Explorer ───
kubectl get pods --all-namespaces
kubectl explain pod

## ─── Partie 4 : Namespace anfa ───
kubectl create namespace anfa
kubectl config set-context --current --namespace=anfa
kubectl get pods                # vide pour l'instant

## ─── Partie 5 : Déployer MinIO ───
kubectl apply -f manifests/minio-pvc.yaml
kubectl get pvc                 # statut Bound

kubectl apply -f manifests/minio-deployment.yaml
kubectl get pods -w             # Pending → ContainerCreating → Running (Ctrl+C)
kubectl get deployment minio    # 1/1 ready
kubectl logs deployment/minio   # chercher "API: http://...:9000"

kubectl apply -f manifests/minio-service.yaml
kubectl get service minio       # NodePort 30900/30901

## ─── Partie 5.5 : Accéder à la console (2 terminaux séparés) ───
# Terminal A :
kubectl port-forward service/minio 9001:9001
# Terminal B :
kubectl port-forward service/minio 9000:9000
# Navigateur : http://localhost:9001  (anfa-admin / anfa-password-2026)
# >>> CAPTURE 1 : console-minio.png <<<

## ─── Partie 6 : Self-healing ───
kubectl get pods                # noter le nom du pod, ex: minio-xxxx-yyyy
kubectl delete pod <NOM-DU-POD> # remplacer par le vrai nom
kubectl get pods -w             # voir l'ancien Terminating + nouveau créé (Ctrl+C)
kubectl get pods                # >>> CAPTURE 2 : self-healing.png <<<

## ─── Partie 7 : Scaling ───
kubectl scale deployment minio --replicas=3
kubectl get pods -w             # voir 2 nouveaux pods (Ctrl+C)
kubectl get pods                # >>> CAPTURE 3 : scaling-3-replicas.png <<<
kubectl get deployment minio    # 3/3
kubectl scale deployment minio --replicas=1   # retour à 1

## ─── Partie 8 : Ingress Controller (aperçu) ───
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=300s
kubectl get pods -n ingress-nginx   # ingress-nginx-controller Running

## ─── Partie 10 : Commit et push ───
cd ..
git add seance-03/
git commit -m "Seance 3 : Deploiement de MinIO sur Kubernetes avec Kind"
git push -u origin seance-03

## Lien à soumettre dans Google Classroom :
## https://github.com/seenam/cloud-bigdata-anfa-resources/tree/seance-03
