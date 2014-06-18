

Thanks
======

This is the code of http://fixmystreet.irisnet.be project stand at https://github.com/CIRB/django-fixmystreet.

It is a fork of http://fixmystreet.ca (https://github.com/visiblegovernment/django-fixmystreet), thank you to them for providing this great project !

This project in place use Urbis for map, search and locate engine (http://geoserver.gis.irisnet.be/).

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

Ensure libxml2-dev, psycopg2 and GeoDjango are installed.

For GeoDjango installation:

https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/

may be incompatibility between postgis and psycopg2 on postgresql 9.1
if message is like "invalid byte sequence for encoding UTF8: 0x00"
need to apply this patch:

https://code.djangoproject.com/ticket/16778


This project has been developed and tested with PostgreSQL

To install GeoDjango for PostgreSQL:

- GEOS https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#geos
- PROJ.4 https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#proj4
- PostGIS https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#postgis
- (install psycopg2?)
- Create PostGIS template https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#spatialdb-template


After install, create the database and init the cache:

```bash

$ make createdb
$ make initcache
$ bin/django loaddata sample # if you want some sample data to work with
$ cp local_settings_staging.py local_settings.py # and edit db connection settings
```

Recreate the database from clean state:

```bash
$ make scratchdb # also import default and samples data.
```

In deploy environment, settings are given by system environment variables.

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

To initialize variables on the server:

```bash
$ . ~/env
```




Continuous Integration, Deployment and Delivery
===============================================

Jenkins
-------

This project is tested under the Jenkins CI at http://jenkins.cirb.lan/job/django-fixmystreet/
It will be automatically built on every push on GitHub, if tests succeed
the project will be deployed.


Branching tagging and deployment
--------------------------------

dev server will be automatically updated with the latest commit from GitHub,
staging will be automatically updated with the latest tagged commit from GitHub
production will be manually updated with the fixed tagged commit from GitHub


Useful commands
================

To generate po files, run the following command:

    $ django-admin.py makemessages -a -e .html,.txt --ignore=templates/admin/* --ignore=templates/posters.html --ignore=templates/promotions/*
    $ django-admin.py compilemessages

For sample data set loading:

    $ python manage.py loaddata sample.json
    $ cp -Rf media/photos-sample/ media/photos/

    $ python manage.py testserver sample.json

    $ python manage.py dumpdata mainapp.Report mainapp.ReportUpdate mainapp.ReportSubscriber --format json --indent 2 > mainapp/fixtures/sample.json


To generate data model image:

    $ bin/django graph_models fixmystreet -g -o data-model.png


Dump DB:

    pg_dump fixmystreet -U fixmystreet > fixmystreet_dump.sql

Import dump DB:

    dropdb fixmystreet -U postgres
    createdb --template=template_postgis fixmystreet -U postgres -O fixmystreet
    cat fixmystreet_dump.sql | psql -U fixmystreet
