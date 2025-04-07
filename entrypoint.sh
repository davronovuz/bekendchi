#!/bin/sh

# Migratsiyalarni qo‘llash
python manage.py makemigrations
python manage.py migrate

# Gunicorn ni ishga tushirish
exec gunicorn --bind 0.0.0.0:8005 config.wsgi:application