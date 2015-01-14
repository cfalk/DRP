#Instructions written by Casey Falk (5/17/14)
#Last updated by Casey Falk (6/2/14)

#The following instructions are written to work with Ubuntu 12+ and have been tested on Ubuntu 13.

#Install the necessary programs.
sudo apt-get install python-dev python-pip mysql-server python-mysqldb nginx uwsgi uwsgi-plugin-python python-rdkit git virtualenvwrapper weka graphviz memcached python-memcache mailutils

#Note which version of Django gets installed.
sudo pip install numpy scipy Django pygraphviz

sudo easy_install South

# # # !! SKIPPABLE FOR TEST BED!!  # # #
#Install ChemAxon's JChem and Marvin. These do intense, high-level chem-calcs for us. Note that these DON'T need to be installed on a test-bed if you don't need to test the compound property calculators.

# # # !! SKIPPABLE FOR TEST BED!!  # # #
#On a production server, use a "cron" job to back up the database (the command "sudo scrontab -e" initiates crontab editor). Note that the password needs to change from what it is below. Ideally the password will be stored more discretely in one place on the server. Add the following line to dump the database to a unique file every day in a DropBox backup folder.
30 3 * * * mysqldump -uroot -p SecurePassword DRP_db > /home/drp/database_backups/Dropbox/DRP_db__$(date +\%m_\%d_\%y).sql

#Likewise, set up nginx to start every hour in case it goes happens to go down.
0 * * * * service nginx start

#And back up the models directory each day.
0 3 * * * cp -rn /home/drp/web/darkreactions.haverford.edu/app/DRP/models/* /home/drp/model_backups/


# # # !! SKIPPABLE FOR TEST BED!!  # # #
#Install a virtualenv if you are on the production server. This helps prevent hackers from accessing file and system information outside of the directory of the project.

#Set the "root" user password to "SecurePassword" (or something more secure if in production) so that you don't forget it and it has no correlation with the project itself. You should get prompted.

#The URL below might change depending on your username.
git clone git@bitbucket.org:darkreactionproject/dark-reaction-site.git

# # # !! SKIPPABLE FOR TEST BED!!  # # #
#Move the NGINX and UWSGI files to their appropriate directories. Note that in development, you can just the the Django runserver (command: "python manage.py runserver") and thus can skip anything related to nginx/uwsgi.
sudo mv DRP_nginx aetc/nginx/sites-available/DRP_nginx
sudo mv DRP_uwsgi /etc/uwsgi/apps-available/DRP_uwsgi

# # # !! SKIPPABLE FOR TEST BED!!  # # #
#Set up "sym links" so that the files are "activated." This is good practice so that the actual configuration file itself is never discarded when a site is de-activated.
sudo ln -s /etc/nginx/sites-available/DRP_nginx /etc/nginx/sites-enabled/DRP_nginx
sudo ln -s /etc/uwsgi/apps-available/DRP_uwsgi /etc/uwsgi/apps-enabled/DRP_uwsgi

# # # !! SKIPPABLE FOR TEST BED!!  # # #
#Restart nginx and uwsgi so that they know that we changed files. If we don't, they will continue to distribute the obsolete "cached" versions. This should be done every time a change is made.
sudo services nginx restart
sudo services uwsgi restart

#Copy over a version of the database from the production server or a backup. Choose the most recent mysqldump file to avoid data-loss.
scp drp@darkreactions.haverford.edu:/home/drp/database_backups/Dropbox/DRP_db__03_30_14.sql ./database.sql

#Create an empty database for DRP using the MySQL client:
mysql -uroot -p
mysql> CREATE DATABASE DRP_db;
exit

#Load the mysqldump into this empty DRP database. Note that "SecurePassword" should be more secure in production.
mysql -u root --password=SecurePassword DRP_db < database.sql

#Remove any migration history that might exist. BE CAREFUL WHAT YOU DELETE.
rm -r DRP/migrations/

#Convert the database to be managed by South. The last "--fake" and "--delete-ghost-migrations" options specify that the database version that South has stored in its personal database tables should be ignored.
python manage.py syncdb
python manage.py convert_to_south DRP
python manage.py migrate DRP --fake --delete-ghost-migrations

# # # !! ONLY RUN WHEN DJANGO MODELS CHANGE !!  # # #
#When you change a model changes or add a field, you must run the following two commands. They'll also need to be run on the production server. Be warned that if you change the Django models before South is loaded, it may blow up on you.
python manage.py schemamigration --auto DRP
python manage.py migrate DRP

#At this point, you should have a fully-functional production-bed or test-bed.
#Production: Verify by going to wherever the webapp are served (darkreactions.haverford.edu by default)
#Development: Verify by running "python manage.py runserver 0.0.0.0:8000" and going to port 8000 on the server hosting your workspace.