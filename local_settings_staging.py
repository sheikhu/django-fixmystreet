import os

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

TEMPLATE_DIRS = (os.path.join(PROJECT_PATH, 'templates-bxl'))
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media-bxl')

#GEOS_LIBRARY_PATH = '/usr/local/lib/libgeos_c.so'

DATABASE_ENGINE = "postgresql_psycopg2"
DATABASE_NAME = "fixmystreet"
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "password"
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5432'


#EMAIL_USE_TLS =
EMAIL_HOST = "relay.irisnet.be"
#EMAIL_HOST_USER =
#EMAIL_HOST_PASSWORD =
#EMAIL_PORT =
EMAIL_ADMIN = "jsanchezpando@cirb.irisnset.be"
ADMIN_EMAIL = "jsanchezpando@cirb.irisnset.be"
ADMIN = ["Jonathan"]

EMAIL_FROM_USER = "django@cirb.irisnet.be"
DEFAULT_FROM_EMAIL = "django@cirb.irisnset.be"

DEBUG = True
SITE_ID = 1
LOCAL_DEV = True
SITE_URL = "http://192.168.103.27:8000"

GEOSERVER = "geoserver.gis.irisnetlab.be"
LOCAL_API = "192.168.13.42" # gislb.irisnetlab.be

#SECRET_KEY=
#GMAP_KEY=
