import os
import glob

if not os.path.isdir('xchem_db/migrations'):
    raise Exception('No migrations found! Please ensure these are generated so that SQL can be generated.')

if os.path.isdir('xchem_db/migrations'):
    for f in glob.glob('xchem_db/migrations/*.py'):
        if '__init__' not in f:
            migration_name = f.split('/')[-1].replace('.py', '')
            os.system(f'python manage.py sqlmigrate xchem_db {migration_name} > sql/{migration_name}.sql')
