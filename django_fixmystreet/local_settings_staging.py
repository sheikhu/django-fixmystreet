import os

DATABASES = {
   'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
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

EMAIL_HOST = "relay.irisnet.be"
EMAIL_ADMIN = "###@cirb.irisnet.be"
ADMIN_EMAIL = "###@cirb.irisnet.be"

FACEBOOK_API_SECRET         = '###'

GOOGLE_OAUTH2_CLIENT_ID     = '###'
GOOGLE_OAUTH2_CLIENT_SECRET = '###'


