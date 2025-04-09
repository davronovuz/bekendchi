#!/bin/bash

# Django migrations’larni bajarish
python manage.py makemigrations
python manage.py migrate

# Gunicorn serverini ishga tushirish
exec gunicorn --bind 0.0.0.0:8005 config.wsgi:application