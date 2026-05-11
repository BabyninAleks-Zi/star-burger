#!/usr/bin/env bash

set -e

echo "Deploying Star Burger..."

cd /srv/star-burger/app

echo "Pulling latest code..."
git pull --ff-only

echo "Installing Python dependencies..."
/srv/star-burger/app/venv/bin/python -m pip install -r requirements.txt

echo "Using Node.js 16.16.0..."
export NVM_DIR="/root/.nvm"
source "$NVM_DIR/nvm.sh"
nvm use 16.16.0

echo "Installing Node.js dependencies..."
npm ci --no-audit --no-fund

echo "Building frontend bundles..."
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo "Collecting Django static files..."
/srv/star-burger/app/venv/bin/python manage.py collectstatic --noinput

echo "Applying database migrations..."
/srv/star-burger/app/venv/bin/python manage.py migrate --noinput

echo "Restarting Gunicorn service..."
systemctl restart star-burger
systemctl is-active --quiet star-burger

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
