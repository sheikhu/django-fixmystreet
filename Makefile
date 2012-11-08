.PHONY        = install deploy test run jenkins rpm clean
APP_NAME      = fixmystreet
# backoffice
BIN_DIR       = bin
LIBS_DIR      = libs

RPM_VERSION   = test
RPM_URL       = https://github.com/CIRB/Monitoring-Des-Quartiers
RPM_USER      = fixmystreet
RPM_GROUP     = fixmystreet
RPM_NAME      = fixmystreet
RPM_PREFIX    = /home/fixmystreet/django-fixmystreet
RPM_INPUTS_FILE = rpm-include-files

$(BIN_DIR)/buildout: $(LIBS_DIR)
	wget http://svn.zope.org/*checkout*/zc.buildout/tags/1.4.4/bootstrap/bootstrap.py
	python bootstrap.py

$(LIBS_DIR):
	mkdir $(LIBS_DIR)

# deploy: $(BIN_DIR)/buildout
	# $(BIN_DIR)/buildout install django

install: $(BIN_DIR)/buildout
	$(BIN_DIR)/buildout -Nvt 5

init:
	$(BIN_DIR)/bin/django syncdb --migrate


test: $(BIN_DIR)/django
	cp -Rf media/photos-sample/ media/photos/
	ENV=dev $(BIN_DIR)/django test $(APP_NAME)

jenkins: $(BIN_DIR)/django
	cp -Rf media/photos-sample/ media/photos/
	find django_fixmystreet -name "*.py" | egrep -v '^django_fixmystreet/*/tests/' | xargs bin/pyflakes > pyflakes.log
	ENV=jenkins $(BIN_DIR)/django-jenkins jenkins $(APP_NAME)

rpm:
	find . -type f -name "*.pyc" -delete
	fpm -s dir -t rpm -n $(RPM_NAME) \
			--url $(RPM_URL) \
			--rpm-user $(RPM_USER) \
			--rpm-group $(RPM_GROUP) \
			-v $(RPM_VERSION) \
			--prefix $(RPM_PREFIX) \
			--after-install after-install.sh \
			`cat $(RPM_INPUTS_FILE)`


initdb:
	sh initpgdb.sh

clean:
	rm -rf bootstrap.py \
			$(BIN_DIR) \
			$(LIBS_DIR)
