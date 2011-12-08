
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
requirements: transmeta, stdimage, GeoDjango

    $ easy_install django-transmeta
    $ easy_install django-stdimage

for GeoDjango installation:
https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/


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


Usefull
-------
To generate po file run the following command:
    $ django-admin.py makemessages -a -e .html,.txt --ignore=templates/* --ignore=templates-bxl/admin/* --ignore=templates-bxl/posters.html --ignore=templates-bxl/promotions/*
    $ django-admin.py compilemessages

for sample data set loading
    $ python manage.py loaddata sample.json
    $ cp -R media-bxl/photos-sample/ media-bxl/photos/

    $ python manage.py testserver sample.json

    $ python manage.py dumpdata mainapp.Report mainapp.ReportUpdate mainapp.ReportSubscriber --format json --indent 2 > mainapp/fixtures/sample.json


To build a mobile app:
* build a new project with phone gap
* drop content of media-bxl/mobile-app/ into www phongap folder
* copy media-bxl/js/fixmystreetmap.js into www phongap folder
* for ios: put geoserver.gis.irisnet.be and fixmystreet.irisnet(lab).be into the externalHost in the phonegap.plist file




To fix ios and android picture exif header orientation browser unsuported, normalize the orientation of the photo before the resize.

in stdimage/fields.py
def get_exifs(img):
    from PIL import Image
    from PIL.ExifTags import TAGS

    ret = {}
    info = img._getexif()
    if(not info):
        return ret
    #import pdb;pdb.set_trace()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret


in stdimage/fields.py function _resize_image
    exifs = get_exifs(img)
    orientation = 1
    if('Orientation' in exifs):
        orientation = exifs['Orientation']

    if(orientation == 3 or orientation == 4):
        img = img.rotate(180)
    elif(orientation == 5 or orientation == 6):
        img = img.rotate(-90)
    elif(orientation == 7 or orientation == 8):
        img = img.rotate(90)
    
    if(orientation == 2 or orientation == 4 or orientation == 5 or orientation == 7):
        img = ImageOps.mirror(img)
