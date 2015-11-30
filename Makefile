.PHONY        = install init html-doc install develop test jenkins createdb dropdb scratchdb clean
APP_NAME      = apps.fixmystreet apps.backoffice apps.fmsproxy
INSTALL_PATH  = $(abspath env)
BIN_PATH      = $(INSTALL_PATH)/bin
SRC_ROOT      = apps

USER          = fixmystreet
GROUP         = fixmystreet
SOURCE_URL    = https://github.com/CIRB/django-fixmystreet

RPM_VERSION   = test
RPM_NAME      = fixmystreet
RPM_PREFIX    = /home/fixmystreet/fixmystreet
RPM_INPUTS_FILE = rpm-include-files

DBNAME        = fixmystreet
DBUSER        = fixmystreet

$(BIN_PATH):
	echo $(BIN_PATH)
	virtualenv --python=python2.7 $(INSTALL_PATH) --system-site-packages
	curl https://bootstrap.pypa.io/ez_setup.py | $(BIN_PATH)/python
	curl https://bootstrap.pypa.io/get-pip.py  | $(BIN_PATH)/python

clean:
	rm -rf $(INSTALL_PATH)
	rm -rf reports
	rm -rf static
	rm -rf *.egg-info
	rm -rf setuptools-*.zip

collectstatic:
	$(BIN_PATH)/manage.py collectstatic --noinput

develop: $(BIN_PATH)
	$(BIN_PATH)/python setup.py develop -Z
	$(BIN_PATH)/pip install -e .[dev]
	$(MAKE) migrate

dropdb:
	dropdb $(DBNAME) -U $(DBUSER)

fixmystreet/local_settings.py:
	cp fixmystreet/local_settings_staging.py fixmystreet/local_settings.py
	edit fixmystreet/local_settings.py

initcache:
	$(BIN_PATH)/manage.py createcachetable fms_cache

install: $(BIN_PATH)
	$(BIN_PATH)/python setup.py develop -Z
	$(MAKE) migrate collectstatic

jenkins: develop
	rm -rf reports
	mkdir reports
	$(BIN_PATH)/flake8 --exclude migrations $(SRC_ROOT) > reports/flake8.report || echo "lint errors"
	$(BIN_PATH)/manage.py jenkins $(APP_NAME)

lint:
	$(BIN_PATH)/flake8 --exclude migrations $(SRC_ROOT) || echo "lint errors"

messages:
	cd $(SRC_ROOT); $(BIN_PATH)/manage.py makemessages -l en
	cd $(SRC_ROOT); $(BIN_PATH)/manage.py makemessages -l en -d djangojs
	$(BIN_PATH)/tx push -s
	$(BIN_PATH)/tx pull -a
	cd $(SRC_ROOT); $(BIN_PATH)/manage.py compilemessages

migrate:
	$(BIN_PATH)/manage.py migrate

migrations:
	$(BIN_PATH)/manage.py makemigrations

rpm: clean install
	find . -type f -name "*.pyc" -delete

	python replacer.py `pwd` $(RPM_PREFIX) $(BIN_PATH)
	python replacer.py `pwd` $(RPM_PREFIX) $(INSTALL_PATH)/lib/python2.7/site-packages

	/usr/sbin/prelink --undo $(INSTALL_PATH)/bin/python2.7

	fpm -s dir -t rpm -n "$(RPM_NAME)" -v $(RPM_VERSION) --rpm-user $(RPM_USER) --rpm-group $(RPM_GROUP) --prefix $(RPM_PREFIX) --after-install rpm-migrate.sh `cat $(RPM_INPUTS_FILE)`

run: $(BIN_PATH)
	$(BIN_PATH)/manage.py runserver

test: $(BIN_PATH)/manage.py
	$(BIN_PATH)/manage.py test $(APP_NAME)

test-js:
	testem ci -t apps/fixmystreet/static/tests/index.html

test-js-tdd:
	testem tdd -t apps/fixmystreet/static/tests/index.html
