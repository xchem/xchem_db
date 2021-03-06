![CI - Setup environment, build & add autogenerated files (migrations, SQL & schema image)](https://github.com/xchem/xchem_db/workflows/CI%20-%20Setup%20environment,%20build%20&%20add%20autogenerated%20files%20(migrations,%20SQL%20&%20schema%20image)/badge.svg)
![Release to PyPI](https://github.com/xchem/xchem_db/workflows/Release%20to%20PyPI/badge.svg)


# xchem_db
This repository contains the django models used to generate the XCDB schema.

## To do:
- ~~automate migration on push to main~~
- ~~automate sql on push to main~~
- ~~automate commit to xchem branch on ispyb for sql~~
- automate PR to xchem branch on ispyb for sql

## Getting started
This repository contains everything you should need to develop new models for XChemDB. 

You can develop locally by making use of the containerisation handled in the ``docker-compose`` files here. There are 
two files: (a)``docker-compose.yml`` and (b)``docker-compose.dev.yml``. 

File (a) will create a version of all of the code within the container, which will not dynamically change as the 
directory changes on your local machine.  This file is most useful for automated builds. File (b) will mount the local 
copy of the repository directly into the container, and so is best for development in real-time (locally). This is 
achieved by the inclusion of a volume mount: 

```yaml
volumes:
      - .:/xcdb
```

The docker-compose action will set up two containers that interact with each other. The first container pulls an official 
mariaDB image from dockerhub and runs it under the name ``db``. The second ``xcdb`` container depends on the ``db`` 
container, and contains all of the django code needed to setup the database, and make changes to it. 

To build the containers from ``docker-compose.yml``:

```bash
docker-compose up
```

To build the containers from ``docker-compose.dev.yml``:

```bash
docker-compose -f docker-compose.dev.yml up
```

If the build was successful, you should see the django landing page at ``http://localhost:8000``.

During the setup of the ``db`` container, the ``init.sql`` file is used to pre-populate the database with the tables 
that are expected to exist already (based on the migrations in xchem_db). This is acheived by the following lines in 
the docker-compose file:

```yaml
command: ['--character-set-server=utf8', '--collation-server=utf8_general_ci', '--init-file=/data/application/init.sql']
    volumes:
      - .init.sql:/data/application/init.sql
```

After the ``db`` (database) container has been set up and run, the ``xcdb`` (django) container does the following:
1. Check to see if there are any new models that need to be added to the database and makes the appropriate django 
migration files
2. Applies the migrations to the database (adding/changing tables)
3. Creates a new schema image
4. generates a file under sql containing the sql statements needed to create new tables (mimic of migrations files)
5. Updates the ``init.sql`` file for next time the server is run

This is controlled by:

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

### Useful commands
- To stop the containers, use ``ctrl+C``
- To remove the images use ``docker-compose rm``
- To rebuild the web image use ``docker-compose build .``
- To specify which docker-compose file to use in any command use the ``-f`` flag
- To get into the container use ``docker run -it xcdb /bin/bash``
- To run a command in the web container ``docker-compose run web <command>``


## Instructions for deploying changes
**UNDER CONSTRUCTION - DEPENDS ON TO DO**

The docker-compose file can be used to create the necessary files to update the database. The files needed by Diamond 
are found in the ``sql/`` directory. 

Once you have updated the models in ``xchem_db/models.py``, you can generate the necessary files by running 
``docker-compose up`` from within the local version of your repository. 

This will ensure that your new models can be added to the database by running the necessary django code.


