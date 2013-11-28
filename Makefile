.PHONY        = install init html-doc deploy test run jenkins rpm createdb dropdb scratchdb clean
APP_NAME      = fixmystreet backoffice
BIN_DIR       = bin
LIBS_DIR      = libs

USER          = fixmystreet
GROUP         = fixmystreet
SOURCE_URL    = https://github.com/CIRB/django-fixmystreet

RPM_VERSION   = test
RPM_NAME      = fixmystreet
RPM_PREFIX    = /home/fixmystreet/django-fixmystreet
RPM_INPUTS_FILE = rpm-include-files

DBNAME        = fixmystreet
DBUSER        = fixmystreet

env:
	virtualenv --python=python2.7 env --system-site-packages

install: env
	env/bin/python setup.py install
	env/bin/manage.py migrate --all
	env/bin/manage.py collectstatic --noinput

develop: env
	env/bin/python setup.py develop
	env/bin/manage.py migrate --all

extra:
	env/bin/pip install -e .[debug]

schemamigration:
	env/bin/manage.py schemamigration fixmystreet --auto

html-doc:
	bin/sphinx-apidoc -fF -o doc/source/gen django_fixmystreet
	bin/sphinx-build -d doc/build/doctrees doc/source doc/build/html

test: env/bin/manage.py
	env/bin/manage.py test $(APP_NAME)

lint:
	find django_fixmystreet -name "*.py" | egrep -v '^django_fixmystreet/*/tests/' | xargs bin/pyflakes

jenkins: env/bin/manage.py
	rm -rf reports
	mkdir reports
	env/bin/manage.py jenkins $(APP_NAME)

rpm:
	find . -type f -name "*.pyc" -delete
	fpm -s dir -t rpm -n $(RPM_NAME) \
			--url $(SOURCE_URL) \
			--rpm-user $(USER) \
			--rpm-group $(GROUP) \
			-v $(RPM_VERSION) \
			--prefix $(RPM_PREFIX) \
			--after-install after-install.sh \
			`cat $(RPM_INPUTS_FILE)`


createdb:
	createdb $(DBNAME) -U $(DBUSER) -T template_postgis
	env/bin/manage.py syncdb --migrate
	env/bin/manage.py loaddata bootstrap list_items applicants staging_data

dropdb:
	dropdb $(DBNAME) -U $(DBUSER)

# for scratching another db call:
# $ make DBNAME=my_fms_db_name scratchdb
scratchdb: dropdb createdb
	cp -Rf media/photos-sample/ media/photos/
	env/bin/manage.py loaddata sample

messages:
	cd django_fixmystreet/fixmystreet; ../../bin/django makemessages -a ; ../../bin/django compilemessages
	cd django_fixmystreet/backoffice; ../../bin/django makemessages -a ; ../../bin/django compilemessages

clean:
	rm -rf env
