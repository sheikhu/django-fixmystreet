
Thanks
======
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


CI, tests & coding organisation
===============================
Jenkins
-------
This project is on de CIRB's Jenkins at http://jenkins.cirb.lan/job/FixMyStreet/
It will be automaticly build on every push on github, if tests failed mails are send,
if tests successed project will be deployed.

requirements-test.pip contains debug and Jenkins test requirements, this is installed only on Jenkins server.
test_settings.py is used for test local_settings, it used environment vars, be sure to set it correctly if you use it
export POSTGISDB=xx.xx.xx.xx
export POSTGISUSER=xxx
export POSTGISPWD=xxx
export FBSECRET=xxx

media folder will be cloned in media-tmp by settings.py for tests because some unit tests modify the folder content.

Branches
--------
NOTE : this is not current branching organisation, need to fix server and Jenkins sync first, currently master is synced with dev.fixmystreet.irisnetlab.be.
NOTE2 : this is draft, not finalized structure


| branch name | description |
|:------------|:------------|
| develop     | developing version of the project, branch off from this branch for features implementation, this branch will be sync with http://dev.fixmystreet.irisnetlab.be on staging. |
| pre-release | beta version of the project, only merge from develop or hot fix may be applied on this branch, this branch will be sync with http://fixmystreet.irisnetlab.be on staging. |
| master      | finale and stable version of the project, only merge from pre-release or hot fix may be applied on this branch, this branch will be sync with http://fixmystreet.irisnet.be on production server. |


Developments needs to be applyed on develop ! not on master !

### ressources
Git Workflow for Agile Teams - http://reinh.com/blog/2009/03/02/a-git-workflow-for-agile-teams.html
A successful Git branching model - http://nvie.com/posts/a-successful-git-branching-model/


Usefull
=======
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

