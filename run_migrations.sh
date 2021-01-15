!#/bin/bash

python3.6 /xcdb/manage.py makemigrations
python3.6 /xcdb/manage.py migrate
python3.6 /xcdb/manage.py makemigrations xchem_db
python3.6 /xcdb/manage.py migrate xchem_db
python3.6 /xcdb/manage.py runserver 0.0.0.0:8000