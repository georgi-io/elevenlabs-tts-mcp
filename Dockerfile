FROM python:3.11-slim

WORKDIR /app

# System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Poetry installieren
RUN pip install poetry==1.6.1

# Poetry konfigurieren (keine virtuelle Umgebung)
RUN poetry config virtualenvs.create false

# Projektdateien kopieren
COPY pyproject.toml poetry.lock README.md ./
COPY src/ /app/src/
COPY .env.example /app/.env

# Abhängigkeiten installieren
RUN poetry install --only main --no-interaction --no-ansi

# Berechtigungen anpassen
RUN chmod -R 755 /app

# Port, auf dem das Backend läuft, exponieren
EXPOSE 9020

# Umgebungsvariablen setzen (können durch externe .env oder ENV überschrieben werden)
ENV HOST=0.0.0.0
ENV PORT=9020
ENV BASE_PATH=/jessica-service

# Anwendung starten
CMD ["python", "-m", "src.backend"] 