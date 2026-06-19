#!/bin/sh
# =============================================================================
# Writing System Platform — container entrypoint
# Validates required environment variables, then runs migrations + collectstatic
# before handing off to the actual command (gunicorn, celery, etc.).
# =============================================================================
set -e

# ── Required env var validation ───────────────────────────────────────────────
# Fail fast in production so a misconfigured deploy is obvious immediately
# instead of serving broken responses silently.

check_required() {
  var_name="$1"
  val="$(eval echo "\$$var_name")"
  if [ -z "$val" ]; then
    echo "[entrypoint] ERROR: required environment variable '$var_name' is not set." >&2
    exit 1
  fi
}

if [ "${DJANGO_ENV:-development}" = "production" ]; then
  check_required SECRET_KEY
  check_required POSTGRES_DB_NAME
  check_required POSTGRES_USER_NAME
  check_required POSTGRES_PASSWORD
  check_required REDIS_PASSWORD
  check_required FIELD_ENCRYPTION_KEY
  check_required TOKEN_ENCRYPTION_KEY
  check_required ALLOWED_HOSTS

  # Warn (don't fail) on missing optional-but-recommended vars
  for warn_var in SENTRY_DSN RESEND_API_KEY AWS_STORAGE_BUCKET_NAME; do
    val="$(eval echo "\$$warn_var")"
    if [ -z "$val" ]; then
      echo "[entrypoint] WARN: '$warn_var' is not set — some features may be unavailable." >&2
    fi
  done

  # Reject known-insecure default values
  if [ "$SECRET_KEY" = "dev-insecure-key" ] || echo "$SECRET_KEY" | grep -qi "insecure\|example\|changeme"; then
    echo "[entrypoint] ERROR: SECRET_KEY looks like a development placeholder. Set a real value." >&2
    exit 1
  fi
fi

# ── Web-only preparation (migrations + static) ────────────────────────────────
should_prepare_web="false"

if [ "$1" = "gunicorn" ] || [ "$1" = "daphne" ]; then
    should_prepare_web="true"
elif [ "$1" = "python" ] && [ "$2" = "manage.py" ] && [ "$3" = "runserver" ]; then
    should_prepare_web="true"
fi

if [ "$should_prepare_web" = "true" ]; then
    echo "[entrypoint] Running Django system check..."
    # --deploy checks production-hardened settings; skip it in development
    if [ "${DJANGO_ENV:-development}" = "production" ]; then
        python manage.py check --deploy 2>&1 | grep -v "^System check" || true
    else
        python manage.py check 2>&1 | grep -v "^System check" || true
    fi

    if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
        echo "[entrypoint] Running migrations..."
        python manage.py migrate --noinput
    fi

    if [ "${RUN_COLLECTSTATIC:-}" = "true" ] || [ "${DJANGO_ENV:-}" = "production" ]; then
        echo "[entrypoint] Collecting static files..."
        python manage.py collectstatic --noinput --clear
    fi
fi

echo "[entrypoint] Starting: $*"
exec "$@"
