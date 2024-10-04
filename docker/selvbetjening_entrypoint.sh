#!/bin/bash
set -e

MAKE_MIGRATIONS=${MAKE_MIGRATIONS:=false}
MIGRATE=${MIGRATE:=false}
DJANGO_DEBUG=${DJANGO_DEBUG:=false}
SKIP_IDP_METADATA=${SKIP_IDP_METADATA:=false}

python manage.py wait_for_db
python manage.py createcachetable
if [ "${SKIP_IDP_METADATA,,}" = false ]; then
  python manage.py update_mitid_idp_metadata
fi
if [ "${MAKE_MIGRATIONS,,}" = true ]; then
  echo 'generating migrations'
  python manage.py makemigrations
fi
if [ "${MIGRATE,,}" = true ]; then
  echo 'running migrations'
  python manage.py migrate
fi
exec "$@"
