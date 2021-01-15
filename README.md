# xchem_db
This repository contains the django models used to generate the XCDB schema.

## To do:
- automate migration on push to main
- automate sql on push to main
- automate commit to xchem branch on ispyb for sql
- automate PR to xchem branch on ispyb for sql

## Development
The docker-compose file can be used to create the neccessary files to update the database. The files needed by Diamond 
are found in the ``sql/`` directory. 

Once you have updated the models in ``xchem_db/models.py``, you can generate the neccessary files by running 
``docker-compose up`` from within the local version of your repository. 

This will ensure that your new models can be added to the database by running the necessary django code.

The way this is acheived is shown in the docker-compose file section below.

## Instructions for deploying changes
UNDER CONSTRUCTION - DEPENDS ON TO DO

## docker-compose file

```yaml
command: ['--character-set-server=utf8', '--collation-server=utf8_general_ci', '--init-file=/data/application/init.sql']
    volumes:
      - .init.sql:/data/application/init.sql
```

``init.sql`` is a concatenated version of all of the files in ``sql/``. This sets up the database as if all existing 
migrations have been run

```yaml
command: >
      /bin/bash -c "python3.6 manage.py makemigrations &&
      python3.6 manage.py migrate &&
      python3.6 manage.py makemigrations xchem_db &&
      python3.6 manage.py migrate xchem_db &&
      python3.6 manage.py graph_models -a -o schema.png &&
      python3.6 run_sql_gen.py &&
      python3.6 compile_init.py &&
      python3.6 manage.py runserver 0.0.0.0:8000"
```

after the ``db`` (database) container has been set up and run, the ``web`` (django) container does the following:
1. Check to see if there are any new models that need to be added to the database and makes the appropriate django 
migration files
2. Applies the migrations to the database (adding/changing tables)
3. Creates a new schema image
4. generates a file under sql containing the sql statements needed to create new tables (mimic of migrations files)
5. Updates the ``init.sql`` file for next time the server is run
