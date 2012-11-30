.PHONY        = install init deploy test run jenkins rpm createdb dropdb scratchdb clean
APP_NAME      = fixmystreet backoffice
BIN_DIR       = bin
LIBS_DIR      = libs

USER          = fixmystreet
GROUP         = fixmystreet
SOURCE_URL    = https://github.com/CIRB/Monitoring-Des-Quartiers

RPM_VERSION   = test
RPM_NAME      = fixmystreet
RPM_PREFIX    = /home/fixmystreet/django-fixmystreet
RPM_INPUTS_FILE = rpm-include-files

DBNAME        = fixmystreet

bootstrap.py:
	wget http://svn.zope.org/*checkout*/zc.buildout/tags/1.4.4/bootstrap/bootstrap.py
	mkdir $(LIBS_DIR)

$(BIN_DIR)/buildout: bootstrap.py
	python bootstrap.py

# deploy: $(BIN_DIR)/buildout
	# $(BIN_DIR)/buildout install django

install: $(BIN_DIR)/buildout
	$(BIN_DIR)/buildout -Nvt 5

init:
	$(BIN_DIR)/django syncdb --migrate --noinput


test: $(BIN_DIR)/django
	$(BIN_DIR)/django test $(APP_NAME)

lint:
	find django_fixmystreet -name "*.py" | egrep -v '^django_fixmystreet/*/tests/' | xargs bin/pyflakes

jenkins: $(BIN_DIR)/django
	rm -rf reports
	mkdir reports
	$(BIN_DIR)/django-jenkins jenkins $(APP_NAME)

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
	createdb $(DBNAME) -U $(USER) -T template_postgis
	$(BIN_DIR)/django syncdb --migrate --noinput
	$(BIN_DIR)/django loaddata bootstrap list_items

dropdb:
	dropdb $(DBNAME) -U $(USER)

# for scratching another db call:
# $ make DBNAME=my_fms_db_name scratchdb
scratchdb: dropdb createdb
	cp -Rf media/photos-sample/ media/photos/
	$(BIN_DIR)/django loaddata sample

clean:
	rm -rf bootstrap.py \
			$(BIN_DIR) \
			$(LIBS_DIR) \
			src
