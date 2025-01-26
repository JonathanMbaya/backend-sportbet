# Commande pour démarrer l'application Flask
# CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]


# Utilise une image Python officielle comme base
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

COPY requirements.txt requirements.txt

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers de l'application Flask
COPY . .

# Exposer le port sur lequel Flask va tourner
EXPOSE 5001

CMD ["python", "run.py"]

