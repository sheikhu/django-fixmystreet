

Thanks
======

This is the code of http://fixmystreet.irisnet.be project stand at https://github.com/CIRB/django-fixmystreet.

It is a fork of http://fixmystreet.ca (https://github.com/visiblegovernment/django-fixmystreet), thank you to them for providing this great project !

this project in place use Urbis for map, search and locate engine (http://geoserver.gis.irisnet.be/).

[the technical documentation](http://fixmystreet.irisnetlab.be/admin/doc/)

[![data model](https://raw.github.com/CIRB/django-fixmystreet/master/data-model.png)](http://fixmystreet.irisnetlab.be/admin/doc/)


Installation
============

```bash
$ git clone git@github.com:CIRB/django-fixmystreet.git
$ make install
$ bin/django runserver
$ bin/django-debug runserver # debug toolbar mode 
```

enchure libxml2-dev, psycopg2 and GeoDjango is installed

for GeoDjango installation:

https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/

may be incompatibility between postgis and psycopg2 on postgresql 9.1
if message is like "invalid byte sequence for encoding UTF8: 0x00"
need to apply this patch:

https://code.djangoproject.com/ticket/16778


this project has been developped and tested with PostgreSql

to install GeoDjango for PostgreSql:

- GEOS https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#geos
- PROJ.4 https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#proj4
- PostGIS https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#postgis
- (install psycopg2?)
- Create PostGIS template https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#spatialdb-template


after install, create the database:

```bash

$ make createdb 
$ bin/django loaddata sample # if you want some sample data to work with 
$ cp local_settings_staging.py local_settings.py # and edit db connection settings 
```

recreate the database from clean state:

```bash
$ make scratchdb # also import default and samples data. 
```

In deploy environment, settings are given by system environment variable.

Available variables:

```bash
ENV # environment that is running, supported values are local / dev / staging / production
ADD_THIS_KEY # code from add_this service
MEDIA_ROOT # path to dynamic files upload location
GA_CODE # code Google Analytic

# database variables
DATABASE_ENGINE
DATABASE_NAME
DATABASE_USER
DATABASE_PASSWORD
DATABASE_PORT
DATABASE_HOST 
```

To initialize variables on the server

```bash
$ . ~/env
```




Continuous Integration, Deployment and Delivery
===============================================

Jenkins
-------

This project is tested under de Jenkins CI at http://jenkins.cirb.lan/job/django-fixmystreet/
It will be automaticly build on every push on github, if tests successed
project will be deployed.


branching tagging and deployment
--------------------------------

dev server will be automatically updated with the latest commit from github,
staging will be automatically updated with the latest tagged commit from github
production will be manually updated with the fixed tagged commit from github


Usefull commands
================

To generate po file run the following command:

    $ django-admin.py makemessages -a -e .html,.txt --ignore=templates/admin/* --ignore=templates/posters.html --ignore=templates/promotions/*
    $ django-admin.py compilemessages

for sample data set loading

    $ python manage.py loaddata sample.json
    $ cp -Rf media/photos-sample/ media/photos/

    $ python manage.py testserver sample.json

    $ python manage.py dumpdata mainapp.Report mainapp.ReportUpdate mainapp.ReportSubscriber --format json --indent 2 > mainapp/fixtures/sample.json


generate data model image

    $ bin/django graph_models fixmystreet -g -o data-model.png


open external connexion to pg:

    /var/lib/pgsql/data/pg_hba.conf


To build a mobile app:
* build a new project with phone gap
* drop content of media/mobile-app/ into www phongap folder
* copy media/js/fixmystreetmap.js into www/js phongap folder
* for ios: put geoserver.gis.irisnet.be and fixmystreet.irisnet(lab).be into the externalHost in the phonegap.plist file

dump DB

    pg_dump fixmystreet -U fixmystreet > fixmystreet_dump.sql

import dump DB

    dropdb fixmystreet -U postgres
    createdb --template=template_postgis fixmystreet -U postgres -O fixmystreet
    cat fixmystreet_dump.sql | psql -U fixmystreet
    
TEST
