#!/bin/bash
set -e
MAKE_MIGRATIONS=${MAKE_MIGRATIONS:=false}
MIGRATE=${MIGRATE:=false}
TEST=${TEST:=false}

if [ "$ONESHOT" = true ] || [ "$TEST" = true ] || [ "$MAKE_MIGRATIONS" = true ]; then
  python manage.py wait_for_db
  if [ "$MAKE_MIGRATIONS" = true ]; then
    echo 'generating migrations'
    python manage.py makemigrations
  fi
  if [ "$MIGRATE" = true ]; then
    echo 'running migations'
    python manage.py migrate
  fi
  if [ "$TEST" = true ]; then
    echo 'running tests!'
    exec python manage.py test
  fi
else
  exec "$@"
fi
