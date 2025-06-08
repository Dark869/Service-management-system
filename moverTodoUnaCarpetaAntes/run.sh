#!/usr/bin/env bash
sleep 10

python -u manage.py makemigrations
python -u manage.py migrate

gunicorn --bind :8000 services_management_system.wsgi:application --reload
