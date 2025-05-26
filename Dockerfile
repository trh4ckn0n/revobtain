FROM python:3.11-slim

# Installer socat + dépendances
RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

# Installer Flask
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copier les fichiers du projet
COPY . /app
WORKDIR /app

# Port d'écoute
EXPOSE 10000

CMD ["python", "app.py"]
