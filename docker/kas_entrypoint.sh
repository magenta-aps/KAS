#!/bin/bash
set -e
MAKE_MIGRATIONS=${MAKE_MIGRATIONS:=false}
MIGRATE=${MIGRATE:=false}
TEST=${TEST:=false}
CREATE_USERS=${CREATE_USERS:=false}
DUMMYDATA=${DUMMYDATA:=false}
DJANGO_DEBUG=${DJANGO_DEBUG:=false}

if [ "$MAKE_MIGRATIONS" = true ] || [ "$MIGRATE" = true ] || [ "$TEST" = true ] || [ "$CREATE_USERS" = true ] || [ "$CREATE_DUMMY_USERS" = true ] || [ "$DUMMYDATA" = true ]; then
  python manage.py wait_for_db
  if [ "$MAKE_MIGRATIONS" = true ]; then
    echo 'generating migrations'
    python manage.py makemigrations
  fi
  if [ "$MIGRATE" = true ]; then
    echo 'running migations'
    python manage.py migrate
  fi
  if [ "$CREATE_USERS" = true ]; then
    echo 'creating users'
    python manage.py create_rest_user ${REST_TOKEN}
    if [ "x${ADMIN_PASSWORD}" != "x" ]; then
      echo 'Create admin user / setting admin password'
      python manage.py create_admin_user ${ADMIN_PASSWORD}
    fi
    if [ "$CREATE_DUMMY_USERS" ]; then
      echo 'Create dummy users'
      python manage.py create_dummy_users
    fi
  fi
  if [ "$CREATE_DUMMY_USERS" = true ]; then
    echo 'Create dummy users'
    python manage.py create_dummy_users
  fi
  if [ "$TEST" = true ]; then
    echo 'running tests!'
    python manage.py test
  fi
  if [ "$DUMMYDATA" = true ]; then
    echo 'creating dummy data!'
    python manage.py create_dummy_data
  fi
fi

if [ "$DJANGO_DEBUG" = false ]; then
  echo 'collecting static files for whitenoise!'
  ./manage.py collectstatic --no-input --clear
fi
exec "$@"
