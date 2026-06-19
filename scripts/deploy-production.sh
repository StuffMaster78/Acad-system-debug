#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

COMPOSE=(
  docker compose
  --env-file .env
  -f docker-compose.yml
  -f docker-compose.prod.yml
)

PRIMARY_DOMAIN="${PRIMARY_DOMAIN:-writerscreek.com}"
RELEASE_ENV=".env.next"
PREVIOUS_ENV=".env.previous"
DEPLOY_SUCCEEDED=false

rollback() {
  if [[ "$DEPLOY_SUCCEEDED" == "true" ]]; then
    return
  fi
  echo "Deployment failed; attempting rollback."
  if [[ -f "$PREVIOUS_ENV" ]]; then
    cp "$PREVIOUS_ENV" .env
    "${COMPOSE[@]}" pull || true
    "${COMPOSE[@]}" up -d --no-build --remove-orphans || true
  fi
}
trap rollback ERR

if [[ -f "$RELEASE_ENV" ]]; then
  if [[ -f .env ]]; then
    cp .env "$PREVIOUS_ENV"
  fi
  mv "$RELEASE_ENV" .env
  chmod 600 .env
fi

echo "Validating the production Compose model."
"${COMPOSE[@]}" config --quiet

if "${COMPOSE[@]}" ps --status running backup | grep -q backup; then
  echo "Creating a pre-deploy database backup."
  "${COMPOSE[@]}" exec -T backup /usr/local/bin/backup-db.sh
else
  echo "Backup service is not running yet; skipping pre-deploy backup."
fi

echo "Pulling immutable release images."
"${COMPOSE[@]}" pull

echo "Starting database and Redis dependencies."
"${COMPOSE[@]}" up -d db redis

echo "Applying database migrations."
"${COMPOSE[@]}" run --rm web python manage.py migrate --noinput

echo "Starting the release."
"${COMPOSE[@]}" up -d --no-build --remove-orphans

services=(
  web
  portal
  nginx
  writerscreek-web
  gradecrest-web
  nursemygrade-web
  essaymaniacs-web
  researchpapermate-web
)

for service in "${services[@]}"; do
  echo "Waiting for $service to become healthy."
  for attempt in {1..30}; do
    container_id="$("${COMPOSE[@]}" ps -q "$service")"
    status="$(
      docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' \
        "$container_id" 2>/dev/null || true
    )"
    if [[ "$status" == "healthy" ]]; then
      break
    fi
    if [[ "$attempt" == "30" ]]; then
      echo "$service did not become healthy (last status: $status)." >&2
      exit 1
    fi
    sleep 5
  done
done

echo "Running external health and portal-context smoke checks."
curl --fail --silent --show-error --max-time 20 \
  "https://${PRIMARY_DOMAIN}/health/ready/" >/dev/null
curl --fail --silent --show-error --max-time 20 \
  "https://admin.writerscreek.com/api/v1/portal-context/" >/dev/null
curl --fail --silent --show-error --max-time 20 \
  "https://app.writerscreek.com/api/v1/portal-context/" >/dev/null
curl --fail --silent --show-error --max-time 20 \
  "https://app.gradecrest.com/api/v1/portal-context/" >/dev/null

DEPLOY_SUCCEEDED=true
trap - ERR
echo "Production deployment completed successfully."
