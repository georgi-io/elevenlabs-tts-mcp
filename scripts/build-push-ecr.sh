#!/bin/bash
set -e

# Konfigurierbare Variablen
AWS_REGION=${AWS_REGION:-"eu-central-1"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}
ENV=${ENV:-"prod"}
REPO_NAME="jessica"

# Prüfen, ob Colima läuft, wenn nicht, starten
if ! colima status 2>/dev/null | grep -q "running"; then
  echo "Colima ist nicht gestartet. Starte Colima..."
  colima start
fi

echo "Using ECR repository: $REPO_NAME"
echo "Using environment: $ENV"

# Repository URL abrufen
REPO_URL=$(aws ecr describe-repositories --repository-names $REPO_NAME --region $AWS_REGION --query 'repositories[0].repositoryUri' --output text)

if [ $? -ne 0 ]; then
  echo "Fehler: ECR Repository nicht gefunden oder AWS CLI Fehler"
  echo "Stelle sicher, dass das Repository existiert und deine AWS Credentials korrekt sind."
  exit 1
fi

echo "ECR Repository URL: $REPO_URL"

# Login bei ECR - angepasst für Colima ohne Docker Credential Helper
echo "Bei ECR anmelden..."
# Umgehe den Docker Credential Helper mit --password-stdin
AWS_ECR_PASSWORD=$(aws ecr get-login-password --region $AWS_REGION)
echo $AWS_ECR_PASSWORD | docker login --username AWS --password-stdin $REPO_URL

# Docker-Image bauen
echo "Docker-Image wird gebaut: $REPO_URL:$IMAGE_TAG"
docker build -t $REPO_URL:$IMAGE_TAG .

# Docker-Image taggen
echo "Docker-Image wird getaggt..."
docker tag $REPO_URL:$IMAGE_TAG $REPO_URL:$IMAGE_TAG

# Docker-Image pushen
echo "Docker-Image wird nach ECR gepusht..."
docker push $REPO_URL:$IMAGE_TAG

echo "Fertig! Image wurde erfolgreich nach $REPO_URL:$IMAGE_TAG gepusht." 