#!/bin/sh
set -e

should_prepare_web="false"

if [ "$1" = "gunicorn" ]; then
    should_prepare_web="true"
elif [ "$1" = "python" ] && [ "$2" = "manage.py" ] && [ "$3" = "runserver" ]; then
    should_prepare_web="true"
fi

if [ "$should_prepare_web" = "true" ]; then
    if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
        python manage.py migrate --noinput
    fi

    if [ "${RUN_COLLECTSTATIC:-}" = "true" ] || [ "${DJANGO_ENV:-}" = "production" ]; then
        python manage.py collectstatic --noinput
    fi
fi

exec "$@"
