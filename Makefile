.PHONY        = install init html-doc install develop test jenkins createdb dropdb scratchdb clean
APP_NAME      = fixmystreet backoffice fmsproxy
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
	curl https://bootstrap.pypa.io/ez_setup.py | $(BIN_PATH)/python
	curl https://bootstrap.pypa.io/get-pip.py  | $(BIN_PATH)/python

collectstatic:
	$(BIN_PATH)/manage.py collectstatic --noinput

django_fixmystreet/local_settings.py:
	cp django_fixmystreet/local_settings_staging.py django_fixmystreet/local_settings.py
	edit django_fixmystreet/local_settings.py

migrate:
	$(BIN_PATH)/manage.py syncdb --migrate

install: $(BIN_PATH)
	$(BIN_PATH)/python setup.py develop -Z
	$(MAKE) migrate collectstatic

develop: $(BIN_PATH)
	$(BIN_PATH)/python setup.py develop -Z
	$(BIN_PATH)/pip install -e .[dev]
	$(MAKE) migrate

run: $(BIN_PATH)
	$(BIN_PATH)/manage.py runserver

# generate new migration script
schemamigration:
	$(BIN_PATH)/manage.py schemamigration $(APP_NAME) --auto

test: $(BIN_PATH)/manage.py
	$(BIN_PATH)/manage.py test $(APP_NAME)
	$(MAKE) test-js

test-js:
	testem ci -t django_fixmystreet/fixmystreet/static/tests/index.html

test-js-tdd:
	testem tdd -t django_fixmystreet/fixmystreet/static/tests/index.html

lint:
	$(BIN_PATH)/flake8 --exclude migrations $(SRC_ROOT) || echo "lint errors"

jenkins: develop
	rm -rf reports
	mkdir reports
	$(BIN_PATH)/flake8 --exclude migrations $(SRC_ROOT) > reports/flake8.report || echo "lint errors"
	$(BIN_PATH)/manage.py jenkins $(APP_NAME)

createdb:
	createdb $(DBNAME) -U $(DBUSER) -T template_postgis

dropdb:
	dropdb $(DBNAME) -U $(DBUSER)


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

initcache:
	$(BIN_PATH)/manage.py createcachetable fms_cache
