#!/usr/bin/env bash

set -e

echo "Deploying Star Burger with Docker..."

cd /srv/star-burger/app

echo "Pulling latest code..."
git pull --ff-only

echo "Creating static and media directories..."
mkdir -p /var/www/star-burger/static
mkdir -p /var/www/star-burger/media

echo "Building Docker images..."
docker compose -f docker-compose.production.yaml build

echo "Building frontend bundles..."
docker compose -f docker-compose.production.yaml run --rm frontend

echo "Collecting Django static files..."
docker compose -f docker-compose.production.yaml run --rm backend python manage.py collectstatic --noinput

echo "Applying database migrations..."
docker compose -f docker-compose.production.yaml run --rm backend python manage.py migrate --noinput

echo "Starting Docker services..."
docker compose -f docker-compose.production.yaml up -d db backend

echo "Checking backend container..."
docker compose -f docker-compose.production.yaml ps backend

echo "Notifying Rollbar about deploy..."

ROLLBAR_ACCESS_TOKEN="$(grep '^ROLLBAR_ACCESS_TOKEN=' star_burger/.env | cut -d '=' -f2- | tr -d '\r')"
ROLLBAR_ENVIRONMENT="$(grep '^ROLLBAR_ENVIRONMENT=' star_burger/.env | cut -d '=' -f2- | tr -d '\r')"
REVISION="$(git rev-parse HEAD)"
LOCAL_USERNAME="$(whoami)"

curl --fail --silent --show-error \
  --header "X-Rollbar-Access-Token: ${ROLLBAR_ACCESS_TOKEN}" \
  --header "Content-Type: application/json" \
  --request POST "https://api.rollbar.com/api/1/deploy/" \
  --data "{\"environment\":\"${ROLLBAR_ENVIRONMENT:-production}\",\"revision\":\"${REVISION}\",\"local_username\":\"${LOCAL_USERNAME}\",\"status\":\"succeeded\"}"

echo
echo "Deploy finished successfully."
