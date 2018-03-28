import os
import shutil

work_dir = os.path.dirname(os.path.realpath(__file__))
# db_file = os.path.join(work_dir, 'db.sqlite3')
# migration_dir = os.path.join(work_dir, 'ccm/ccmapp/migrations')
# if os.path.exists(db_file):
# 	os.remove(db_file)
# if os.path.exists(migration_dir):
#     shutil.rmtree(migration_dir)
os.chdir(work_dir)
os.system('python manage.py makemigrations & '
		  'python manage.py makemigrations ccmapp & '
          'python manage.py migrate')
