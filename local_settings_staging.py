import os
import settings

DATABASES = {
   'default': {
        'ENGINE': 'postgresql_psycopg2',
        'NAME': 'fixmystreet',
        'USER': '###',
        'PASSWORD': '###',
        'HOST': 'localhost',
        'PORT': 5432,
        'OPTIONS': {
            'autocommit': True
        }

   }
}



#EMAIL_USE_TLS =
EMAIL_HOST = "relay.irisnet.be"
#EMAIL_HOST_USER =
#EMAIL_HOST_PASSWORD =
#EMAIL_PORT =
EMAIL_ADMIN = "###@cirb.irisnet.be"
ADMIN_EMAIL = "###@cirb.irisnet.be"
ADMIN = ["Jonathan"]

DEBUG = True
SITE_ID = 2
LOCAL_DEV = False
SITE_URL = "###"

GEOSERVER = "geoserver.gis.irisnetlab.be"
SERVICE_GIS = "service.gis.irisnetlab.be"


FACEBOOK_API_SECRET         = '###'

GOOGLE_OAUTH2_CLIENT_ID     = '###'
GOOGLE_OAUTH2_CLIENT_SECRET = '###'


