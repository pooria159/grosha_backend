#!/bin/bash

echo "Waiting for PostgreSQL..."

while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 0.5
done

echo "PostgreSQL started"

python manage.py migrate
python manage.py collectstatic --noinput

exec "$@"