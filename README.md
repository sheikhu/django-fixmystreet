
[![Requirements Status](https://requires.io/github/CIRB/django-fixmystreet/requirements.png?branch=master)](https://requires.io/github/CIRB/django-fixmystreet/requirements/?branch=master)

Thanks
======

This is the code of http://fixmystreet.irisnet.be project stand at https://github.com/CIRB/django-fixmystreet.

It is a fork of http://fixmystreet.ca (https://github.com/visiblegovernment/django-fixmystreet), thank you to them for providing this great project !

This project in place use Urbis for map, search and locate engine (http://geoserver.gis.irisnet.be/).

[the technical documentation](http://fixmystreet.irisnetlab.be/admin/doc/)

[![data model](https://raw.github.com/CIRB/django-fixmystreet/master/data-model.png)](http://fixmystreet.irisnetlab.be/admin/doc/)


Installation
============

The following instructions will assume that you are starting from a fresh Ubuntu install (or similar).

Preparation
-----------

Start by ensuring that Python "2.7.x" is installed.

If *easy_install* is not installed yet, install it as follows: ```sudo apt-get install python-setuptools```

Use *easy_install* to install *pip*: ```sudo easy_install pip ```

Install the following packages (ubuntu named):

* python-dev
* python-virtualenv
* postgresql-server-dev-9.3
* libgeos-3.4.2
* libgdal1h
* nodejs
* npm
* libjpeg-dev
* libxml2-dev
* python-psycopg2
* binutils
* libproj-dev
* gdal-bin
* postgis
* postgresql-9.3-postgis-2.1
* spatialite-bin

```
sudo apt-get install python-dev python-virtualenv postgresql-server-dev-9.3 libgeos-3.4.2 libgdal1h nodejs npm libjpeg-dev libxml2-dev python-psycopg2 binutils libproj-dev gdal-bin postgis postgresql-9.3-postgis-2.1 spatialite-bin
```

Normally *git*, *make* and *gcc* should be already installed. If not, make sure to install them.

PostgreSQL
----------

Install PostgreSQL using ```sudo apt-get install postgresql```

Create a *fixmystreet* role:

* create a *fixmystreet* role **with a password** on PostgreSQL. The role should be a *superuser*.
* create a *fixmystreet* database for the *fixmystreet* user, owned by *fixmystreet*
* Add *postgis* and *postgis_topology* as an extension to that database
* edit the file *pg_hba.conf* to ensure that *fixmystreet* can access the database without requiring a Linux user: ```/etc/postgresql/9.3/main/pg_hba.conf ```, and in there add the following line ```local all fixmystreet md5``` in the section "*Database administrative login by Unix domain socket*".
* restart the PostgreSQL server: ```sudo /etc/init.d/postgresql restart```

Useful resources:

* [https://help.ubuntu.com/stable/serverguide/postgresql.html](https://help.ubuntu.com/stable/serverguide/postgresql.html)
* [http://www.cyberciti.biz/faq/howto-add-postgresql-user-account/](http://www.cyberciti.biz/faq/howto-add-postgresql-user-account/)

Project setup
-------------

Clone the project:

```
$ git clone git@github.com:CIRB/django-fixmystreet.git
$ make develop
$ make run
```

From "*/django-fixmystreet/fixmystreet_project*" copy the file *local_settings_staging.py* to *local_settings.py*.
Edit it to specify the database credentials:

    DATABASES = {
       'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'fixmystreet',
            'USER': 'fixmystreet',
            'PASSWORD': 'fixmystreet',
            'HOST': 'localhost',
            'PORT': 5432
       }
    }

From the project root folder run ```make develop ``` to retrieve the dependencies and build the project.

You can now ```make run``` to start *FixMyStreet*!

Add data fixtures
-----------------

To add some data to the fresh new database, proceed as follows:

* From the project root folder, enter the virtual environment using ```source env/bin/activate```.
* Add the fixture data using: ```manage.py loaddata apps/fixmystreet/fixtures/*.json```.

Sample of data injected:

```
Organisation entity:    Anderlecht
Users/Password:         leader@anderlecht.be/leader
                        manager@anderlecht.be/manager
Groups:                 groupe

Organisation entity:    Bruxelles-Ville
Users/Password:         leader@bxl.be/leader
                        manager@bxl.be/manager
Groups:                 groupe
```

Additional notes from the previous installation instructions
------------------------------------------------------------

You need a Postgis server, for GeoDjango installation:

https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/

- GEOS https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#geos
- PROJ.4 https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#proj4
- PostGIS https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#postgis
- (install psycopg2?)
- Create PostGIS template https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#spatialdb-template

There may be an incompatibility between postgis and psycopg2 on postgresql 9.1
If this message appears "*invalid byte sequence for encoding UTF8: 0x00*" you might need to apply this patch:

https://code.djangoproject.com/ticket/16778

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
===============

To generate po files, run the following command:

    $ make messages

To generate data model image:

    $ env/bin/manage.py graph_models fixmystreet -g -o data-model.png


Dump DB:

    pg_dump fixmystreet -U fixmystreet > fixmystreet_dump.sql

Import dump DB:

    dropdb fixmystreet -U postgres
    createdb fixmystreet -U postgres -O fixmystreet
    psql fixmystreet -U postgres -c "CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;"
    cat fixmystreet_dump.sql | psql -U fixmystreet
