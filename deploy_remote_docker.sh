#!/usr/bin/env bash

set -euo pipefail

SERVER="${SERVER:-root@77.105.170.71}"
REMOTE_APP_DIR="${REMOTE_APP_DIR:-/srv/star-burger/app}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-app}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.production.yaml}"
DOCKER_HOST="${DOCKER_HOST:-ssh://${SERVER}}"

export DOCKER_HOST

COMPOSE=(docker compose -p "$COMPOSE_PROJECT_NAME" -f "$COMPOSE_FILE")

echo "Deploying Star Burger to remote Docker Engine..."
echo "Docker host: $DOCKER_HOST"
echo "Compose project: $COMPOSE_PROJECT_NAME"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Working tree has uncommitted changes. Commit them before deploy:"
  git status --short
  exit 1
fi

REVISION="$(git rev-parse HEAD)"
LOCAL_USERNAME="$(whoami)"

echo "Checking remote Docker Engine..."
docker info >/dev/null

echo "Creating static and media directories on server..."
ssh "$SERVER" "mkdir -p /var/www/star-burger/static /var/www/star-burger/media"

echo "Building Docker images on remote server from local build context..."
"${COMPOSE[@]}" build

echo "Building frontend bundles..."
"${COMPOSE[@]}" run --rm frontend

echo "Collecting Django static files..."
"${COMPOSE[@]}" run --rm backend python manage.py collectstatic --noinput

echo "Applying database migrations..."
"${COMPOSE[@]}" run --rm backend python manage.py migrate --noinput

echo "Starting Docker services..."
"${COMPOSE[@]}" up -d db backend

echo "Checking backend container..."
"${COMPOSE[@]}" ps backend

echo "Notifying Rollbar about deploy..."

ROLLBAR_ACCESS_TOKEN="$(
  ssh "$SERVER" "grep '^ROLLBAR_ACCESS_TOKEN=' '$REMOTE_APP_DIR/star_burger/.env' | cut -d '=' -f2- | tr -d '\r'"
)"
ROLLBAR_ENVIRONMENT="$(
  ssh "$SERVER" "grep '^ROLLBAR_ENVIRONMENT=' '$REMOTE_APP_DIR/star_burger/.env' | cut -d '=' -f2- | tr -d '\r'"
)"

curl --fail --silent --show-error \
  --header "X-Rollbar-Access-Token: ${ROLLBAR_ACCESS_TOKEN}" \
  --header "Content-Type: application/json" \
  --request POST "https://api.rollbar.com/api/1/deploy/" \
  --data "{\"environment\":\"${ROLLBAR_ENVIRONMENT:-production}\",\"revision\":\"${REVISION}\",\"local_username\":\"${LOCAL_USERNAME}\",\"status\":\"succeeded\"}"

echo
echo "Remote Docker deploy finished successfully."
