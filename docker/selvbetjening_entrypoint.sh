#!/bin/bash
set -e

MAKE_MIGRATIONS=${MAKE_MIGRATIONS:=false}
MIGRATE=${MIGRATE:=false}
DJANGO_DEBUG=${DJANGO_DEBUG:=false}

if [ "$MAKE_MIGRATIONS" = true ] || [ "$MIGRATE" = true ]; then
  python manage.py wait_for_db
  if [ "$MAKE_MIGRATIONS" = true ]; then
    echo 'generating migrations'
    python manage.py makemigrations
  fi
  if [ "$MIGRATE" = true ]; then
    echo 'running migations'
    python manage.py migrate
  fi
fi

if [ "$DJANGO_DEBUG" = false ]; then
  echo 'collection static files for whitenoise!'
  ./manage.py collectstatic --no-input --clear
fi
exec "$@"
