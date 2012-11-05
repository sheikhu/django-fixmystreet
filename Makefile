.PHONY        = install deploy test run jenkins rpm clean
APP_NAME      = fixmystreet
BIN_DIR       = bin
LIBS_DIR      = libs

RPM_VERSION   = test
RPM_URL       = https://github.com/CIRB/Monitoring-Des-Quartiers
RPM_USER      = fms
RPM_GROUP     = fms
RPM_NAME      = monitoring-des-quartiers
RPM_PREFIX    = /home/ibsa/Monitoring-Des-Quartiers
RPM_ITERATION = dev
RPM_INPUTS_FILE = rpm-include-files

$(BIN_DIR)/buildout: $(LIBS_DIR)
	python bootstrap.py

$(BIN_DIR):
	mkdir $(BIN_DIR)

$(LIBS_DIR):
	mkdir $(LIBS_DIR)

# deploy: $(BIN_DIR)/buildout
	# $(BIN_DIR)/buildout install django

install: $(BIN_DIR)/buildout
	$(BIN_DIR)/buildout -Nvt 5

test: $(BIN_DIR)/django
	cp -Rf media/photos-sample/ media/photos/
	$(BIN_DIR)/django test $(APP_NAME)

jenkins: $(BIN_DIR)/django
	cp -Rf media/photos-sample/ media/photos/
	$(BIN_DIR)/django jenkins $(APP_NAME)

rpm:
	find . -type f -name "*.pyc" -delete
	fpm -s dir -t rpm -n $(RPM_NAME) \
			--url $(RPM_URL) \
			--rpm-user $(RPM_USER) \
			--rpm-group $(RPM_GROUP) \
			-v $(RPM_VERSION) \
			--iteration $(RPM_ITERATION) \
			--prefix $(RPM_PREFIX) \
			--after-install after-install.sh \
			`cat $(RPM_INPUTS_FILE)`


initdb:
	sh initpgdb.sh

clean:
	rm -rf bootstrap.py \
			$(BIN_DIR) \
			$(LIBS_DIR)
