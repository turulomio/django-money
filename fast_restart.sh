#!/bin/bash
dropdb -U postgres -h 127.0.0.1 django_money
createdb -U postgres -h 127.0.0.1 django_money
python manage.py migrate
python manage.py createsuperuser
python manage.py migrate_from_xulpymoney --db xulpymoney
python manage.py runserver