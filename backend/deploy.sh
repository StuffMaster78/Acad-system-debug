#!/bin/bash
# =============================================================================
# Writing System Platform — local deploy helper
# Usage: ./deploy.sh [dev|prod]   (default: dev)
#
# For production CI deploys see .github/workflows/deploy-production.yml
# =============================================================================
set -euo pipefail

ENVIRONMENT="${1:-dev}"
COMPOSE_BASE="docker compose"
COMPOSE_PROD="${COMPOSE_BASE} -f ../docker-compose.yml -f ../docker-compose.prod.yml"
COMPOSE_DEV="${COMPOSE_BASE} -f ../docker-compose.yml"

# Run from repo root regardless of where the script is called from
cd "$(dirname "$0")/.." || exit 1

# ── Pre-flight checks ─────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
  echo "ERROR: docker is not installed or not in PATH." >&2; exit 1
fi
if ! docker info &>/dev/null; then
  echo "ERROR: Docker daemon is not running." >&2; exit 1
fi

ENV_FILE="backend/.env"
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: $ENV_FILE not found."
  echo "  cp backend/.env.example backend/.env  then fill in real values."
  exit 1
fi

# Validate critical vars without sourcing (avoids exposing secrets to env)
check_var() {
  local key="$1"
  local val
  val=$(grep -E "^${key}=" "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
  if [ -z "$val" ]; then
    echo "ERROR: '$key' is not set in $ENV_FILE." >&2; exit 1
  fi
  # Reject obvious placeholders
  if echo "$val" | grep -qiE "your-|changeme|insecure|example|placeholder"; then
    echo "ERROR: '$key' looks like a placeholder — set a real value." >&2; exit 1
  fi
}

if [ "$ENVIRONMENT" = "prod" ]; then
  echo "==> Validating production environment..."
  for var in SECRET_KEY POSTGRES_DB_NAME POSTGRES_USER_NAME POSTGRES_PASSWORD \
              REDIS_PASSWORD FIELD_ENCRYPTION_KEY TOKEN_ENCRYPTION_KEY ALLOWED_HOSTS; do
    check_var "$var"
  done
  echo "    All required vars present."
fi

# ── Helper: wait for a service to be healthy ──────────────────────────────────
wait_healthy() {
  local service="$1"
  local compose_cmd="$2"
  local max=30
  echo -n "    Waiting for $service to be healthy"
  for i in $(seq 1 "$max"); do
    status=$(${compose_cmd} ps --format json "$service" 2>/dev/null \
      | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('Health',''))" 2>/dev/null || echo "")
    if [ "$status" = "healthy" ]; then echo " ✓"; return 0; fi
    echo -n "."; sleep 3
  done
  echo " TIMEOUT"
  echo "ERROR: $service did not become healthy in $((max * 3))s." >&2
  exit 1
}

# ── Production deploy ─────────────────────────────────────────────────────────
if [ "$ENVIRONMENT" = "prod" ]; then
  echo "==> Building production images..."
  ${COMPOSE_PROD} build --no-cache web celery beat

  echo "==> Starting services (db + redis first)..."
  ${COMPOSE_PROD} up -d db redis
  wait_healthy db   "${COMPOSE_PROD}"
  wait_healthy redis "${COMPOSE_PROD}"

  echo "==> Starting web, workers, nginx..."
  ${COMPOSE_PROD} up -d --remove-orphans

  wait_healthy web   "${COMPOSE_PROD}"
  wait_healthy nginx "${COMPOSE_PROD}"

  echo "==> Pruning old images..."
  docker image prune -f

  echo "==> Production deploy complete."
  ${COMPOSE_PROD} ps

# ── Development deploy ────────────────────────────────────────────────────────
else
  echo "==> Starting development services..."
  ${COMPOSE_DEV} up -d --build

  wait_healthy db    "${COMPOSE_DEV}"
  wait_healthy redis "${COMPOSE_DEV}"

  echo "==> Development deploy complete."
  echo "    API: http://localhost:8000"
  echo "    Frontend: cd frontend && pnpm dev"
  ${COMPOSE_DEV} ps
fi

echo ""
echo "Logs:  docker compose logs -f"
echo "Stop:  docker compose $( [ "$ENVIRONMENT" = "prod" ] && echo "-f docker-compose.yml -f docker-compose.prod.yml" ) down"
