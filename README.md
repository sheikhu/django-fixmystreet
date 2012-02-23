
Thanks
------
This is the code of http://fixmystreet.irisnet.be project stand at https://github.com/CIRB/django-fixmystreet.

It is a fork of http://fixmystreet.ca (https://github.com/visiblegovernment/django-fixmystreet), thank you to them for providing this great project !

this project in place use Urbis for map, search and locate engine (http://geoserver.gis.irisnet.be/).

installation
============

Installation instructions are available here:
> http://wiki.github.com/visiblegovernment/django-fixmystreet/


(to check)
requirements: transmeta, stdimage, GeoDjango, PIL

    $ easy_install django
    $ easy_install django-transmeta
    $ easy_install django-stdimage
    $ easy_install django-social-auth
    $ easy_install http://effbot.org/downloads/Imaging-1.1.7.tar.gz (???)

may be requied:

    $ easy_install psycopg2==2.4.1


install http://www.pythonware.com/products/pil/ V-1.1.7
pip install PIL


for GeoDjango installation:

https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/

may be incompatibility between postgis and psycopg2 on python2.6
if message is like "invalid byte sequence for encoding UTF8: 0x00"
need to apply this patch:

https://code.djangoproject.com/ticket/16778


this project has been developped and tested with PostgreSql

to install GeoDjango for PostgreSql:
* GEOS https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#geos
* PROJ.4 https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#proj4
* PostGIS https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#postgis
* (install psycopg2?)
* Create PostGIS template https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#spatialdb-template


after install, create the database:
    $ createdb -U postgres -T template_postgis fixmystreet
    $ python manage.py syncdb

if running tests failed with:
    psycopg2.ProgrammingError: autocommit cannot be used inside a transaction
then
    easy_install psycopg2==2.4.1


finally:

    $ cp local_settings_staging.py local_settings.py


Usefull
-------
To generate po file run the following command:
    $ django-admin.py makemessages -a -e .html,.txt --ignore=templates/admin/* --ignore=templates/posters.html --ignore=templates/promotions/*
    $ django-admin.py compilemessages

for sample data set loading
    $ python manage.py loaddata sample.json
    $ cp -Rf media/photos-sample/ media/photos/

    $ python manage.py testserver sample.json

    $ python manage.py dumpdata mainapp.Report mainapp.ReportUpdate mainapp.ReportSubscriber --format json --indent 2 > mainapp/fixtures/sample.json

open external connexion to pg:
    /var/lib/pgsql/data/pg_hba.conf


To build a mobile app:
* build a new project with phone gap
* drop content of media/mobile-app/ into www phongap folder
* copy media/js/fixmystreetmap.js into www/js phongap folder
* for ios: put geoserver.gis.irisnet.be and fixmystreet.irisnet(lab).be into the externalHost in the phonegap.plist file

