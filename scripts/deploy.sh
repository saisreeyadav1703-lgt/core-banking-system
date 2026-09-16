#!/bin/bash
set -euo pipefail
IMAGE_TAG="${1:-latest}"
ENVIRONMENT="${2:-staging}"
echo "Deploying core-banking:${IMAGE_TAG} to ${ENVIRONMENT}..."
docker compose pull
docker compose up -d
sleep 5
curl -sf http://localhost:8080/health && echo "Deployment successful!" || (echo "Health check failed"; exit 1)
