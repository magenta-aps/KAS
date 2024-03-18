#!/bin/bash
set -e
MAKE_MIGRATIONS=${MAKE_MIGRATIONS:=false}
MIGRATE=${MIGRATE:=false}
TEST=${TEST:=false}
CREATE_USERS=${CREATE_USERS:=false}
DUMMYDATA=${DUMMYDATA:=false}
DJANGO_DEBUG=${DJANGO_DEBUG:=false}
MAKEMESSAGES=${MAKEMESSAGES:=true}
COMPILEMESSAGES=${COMPILEMESSAGES:=true}
GENERATE_DB_DOCUMENTATION=${GENERATE_DB_DOCUMENTATION:=true}

if [ "${MAKE_MIGRATIONS,,}" = true ] || [ "${MIGRATE,,}" = true ] || [ "${TEST,,}" = true ] || [ "${CREATE_USERS,,}" = true ] || [ "${CREATE_DUMMY_USERS,,}" = true ] || [ "${DUMMYDATA,,}" = true ] || [ "${MAKEMESSAGES,,}" == true ] || [ "${COMPILEMESSAGES,,}" == true ]; then
  python manage.py wait_for_db
  if [ "${MAKE_MIGRATIONS,,}" = true ]; then
    echo 'generating migrations'
    python manage.py makemigrations
  fi
  if [ "${MIGRATE,,}" = true ]; then
    echo 'running migrations'
    python manage.py migrate
  fi
  if [ "${CREATE_USERS,,}" = true ]; then
    echo 'creating users'
    python manage.py create_rest_user ${REST_TOKEN}
  fi
  if [ "${CREATE_DUMMY_USERS,,}" = true ]; then
    echo 'create dummy users'
    python manage.py create_dummy_users
  fi
  if [ "${TEST,,}" = true ]; then
    echo 'running tests!'
    python manage.py test
  fi
  if [ "${DUMMYDATA,,}" = true ]; then
    echo 'creating dummy data!'
    python manage.py create_dummy_data
  fi
  if [ "${MAKEMESSAGES,,}" = true ]; then
    echo 'making messages!'
    python manage.py makemessages --all --no-obsolete --add-location file
  fi
  if [ "${COMPILEMESSAGES,,}" = true ]; then
    echo 'compiling messages!'
    python manage.py compilemessages
  fi

  if [ "${GENERATE_DB_DOCUMENTATION,,}" = true ]; then
      echo 'building DB documentation!'
      python manage.py graph_models eskat kas prisme worker -g -X Historical* -o kas/static/doc/kas_models.png
  fi
fi
exec "$@"
