.PHONY        = install init html-doc install develop test jenkins createdb dropdb scratchdb clean
APP_NAME      = fixmystreet backoffice
INSTALL_PATH  = $(abspath env)
BIN_PATH      = $(INSTALL_PATH)/bin
SRC_ROOT      = django_fixmystreet

USER          = fixmystreet
GROUP         = fixmystreet
SOURCE_URL    = https://github.com/CIRB/django-fixmystreet

RPM_VERSION   = test
RPM_NAME      = fixmystreet
RPM_PREFIX    = /home/fixmystreet/django-fixmystreet
RPM_INPUTS_FILE = rpm-include-files

DBNAME        = fixmystreet
DBUSER        = fixmystreet

$(BIN_PATH):
	echo $(BIN_PATH)
	virtualenv --python=python2.7 $(INSTALL_PATH) --system-site-packages
	curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | $(BIN_PATH)/python
	curl https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py | $(BIN_PATH)/python

install: $(BIN_PATH)
	$(BIN_PATH)/python setup.py install
	$(BIN_PATH)/manage.py migrate --all
	$(BIN_PATH)/manage.py collectstatic --noinput

develop: $(BIN_PATH)
	$(BIN_PATH)/python setup.py develop
	$(BIN_PATH)/pip install --no-use-wheel -e .[debug]
	$(BIN_PATH)/manage.py migrate --all

# generate new migration script
schemamigration:
	$(BIN_PATH)/manage.py schemamigration fixmystreet --auto

html-doc:
	$(BIN_PATH)/sphinx-apidoc -fF -o doc/source/gen $(SRC_ROOT)
	$(BIN_PATH)/sphinx-build -d doc/build/doctrees doc/source doc/build/html

test: $(BIN_PATH)/manage.py
	$(BIN_PATH)/manage.py test $(APP_NAME)

lint:
	$(BIN_PATH)/flake8 --exclude migrations $(SRC_ROOT) || echo "lint errors"

jenkins: develop
	rm -rf reports
	mkdir reports
	$(BIN_PATH)/flake8 --exclude migrations $(SRC_ROOT) > reports/flake8.report || echo "lint errors"
	$(BIN_PATH)/manage.py jenkins $(APP_NAME)

createdb:
	createdb $(DBNAME) -U $(DBUSER) -T template_postgis
	$(BIN_PATH)/manage.py syncdb --migrate
	$(BIN_PATH)/manage.py loaddata bootstrap list_items applicants staging_data

dropdb:
	dropdb $(DBNAME) -U $(DBUSER)

# for scratching another db call:
# $ make DBNAME=my_fms_db_name scratchdb
scratchdb: dropdb createdb
	cp -Rf media/photos-sample/ media/photos/
	$(BIN_PATH)/manage.py loaddata sample

messages:
	cd $(SRC_ROOT); $(BIN_PATH)/manage.py makemessages -l en
	cd $(SRC_ROOT); $(BIN_PATH)/manage.py makemessages -l en -d djangojs
	$(BIN_PATH)/tx push -s
	$(BIN_PATH)/tx pull -a
	cd $(SRC_ROOT); $(BIN_PATH)/manage.py compilemessages

clean:
	cd $(INSTALL_PATH); rm -rf bin lib lib64 include # virtualenv
	rm -rf bin libs bootstrap.py src # buildout
	rm -rf reports # Jenkins
	rm -rf build dist static
