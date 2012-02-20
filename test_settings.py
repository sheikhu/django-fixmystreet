import os

import settings

DATABASES = {
   'default': {
       'ENGINE': 'postgresql_psycopg2',
       'NAME': 'fixmystreet-test',
       'USER': 'jenkins',
       'PASSWORD': 'jenkins',
       'HOST': '192.168.13.55',
       'PORT': 5432
   }
}



#EMAIL_USE_TLS =
EMAIL_HOST = "relay.irisnet.be"
#EMAIL_HOST_USER =
#EMAIL_HOST_PASSWORD =
#EMAIL_PORT =
EMAIL_ADMIN = "jsanchezpando@cirb.irisnet.be"
ADMIN_EMAIL = "jsanchezpando@cirb.irisnet.be"
ADMIN = ["Jonathan"]

#EMAIL_FROM_USER = "fms@cirb.irisnet.be"
#DEFAULT_FROM_EMAIL = "fms@cirb.irisnset.be"

DEBUG = True
SITE_ID = 2
LOCAL_DEV = False
SITE_URL = "http://dev.fixmystreet.irisnetlab.be"

GEOSERVER = "geoserver.gis.irisnetlab.be"
SERVICE_GIS = "service.gis.irisnetlab.be" # gislb.irisnetlab.be
#SECRET_KEY=
#GMAP_KEY=

FACEBOOK_API_SECRET         = 'xxx'

GOOGLE_OAUTH2_CLIENT_ID     = '985105651100-538gtjuj3lghsf4nmn9n1kbsl0t6rr14.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET = 'xxx'

settings.INSTALLED_APPS += ('django_jenkins',)

PROJECT_APPS = ('fixmystreet',)

JENKINS_TASKS = (
    'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.django_tests',
    'django_jenkins.tasks.run_jslint',
)
