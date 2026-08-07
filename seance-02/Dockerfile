# ── Image de base ─────────────────────────────────────────────────────────
# python:3.11-slim-bookworm = Debian 12 minimal, Python 3.11
# "slim" : sans compilateurs ni bibliothèques de dev (gain ~200 Mo vs full)
FROM python:3.11-slim-bookworm

# ── Variables d'environnement ─────────────────────────────────────────────
# PYTHONDONTWRITEBYTECODE : pas de fichiers .pyc inutiles dans l'image
# PYTHONUNBUFFERED        : logs immédiatement visibles (pas de buffer stdout)
# JAVA_HOME               : requis par PySpark pour trouver le JRE
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# ── Installation de Java (dépendance de PySpark) ──────────────────────────
# --no-install-recommends : évite d'installer des paquets optionnels
# rm -rf /var/lib/apt/lists/* : nettoie le cache apt dans la MÊME couche
#   → si on le mettait dans une RUN séparée, la couche apt resterait en cache
RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jre-headless && \
    rm -rf /var/lib/apt/lists/*

# ── Répertoire de travail ─────────────────────────────────────────────────
WORKDIR /app

# ── ASTUCE CACHE : requirements.txt D'ABORD, code ensuite ────────────────
# Si on faisait COPY . . ici, tout changement de code invaliderait pip install
# En copiant requirements.txt seul, pip install est en cache tant que les
# dépendances ne changent pas — même si on modifie analyse_referentiel.py
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copie du code source ──────────────────────────────────────────────────
# Vient APRÈS pip install → invalidation du cache uniquement si le code change
COPY . .

# ── Commande par défaut ───────────────────────────────────────────────────
CMD ["python", "analyse_referentiel.py"]
