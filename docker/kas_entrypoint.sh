#!/bin/bash
set -e
MAKE_MIGRATIONS=${MAKE_MIGRATIONS:=false}
MIGRATE=${MIGRATE:=false}
TEST=${TEST:=false}
DUMMYDATA=${DUMMYDATA:=false}

if [ "$ONESHOT" = true ] || [ "$TEST" = true ] || [ "$MAKE_MIGRATIONS" = true ] || [ "$DUMMYDATA" = true ]; then
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
    python manage.py test
  fi
  if [ "$DUMMYDATA" = true ]; then
    echo 'creating dummy data!'
    python manage.py create_dummy_data
  fi
else
  exec "$@"
fi
