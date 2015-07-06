import os

# local
#~ DATABASES = {
   #~ 'default': {
        #~ 'ENGINE': 'django.contrib.gis.db.backends.postgis',
        #~ 'NAME': 'fixmystreet',
        #~ 'USER': 'fixmystreet',
        #~ 'PASSWORD': 'fixmystreet',
        #~ 'HOST': 'localhost',
        #~ 'PORT': 5432,
        #~ 'OPTIONS': {
            #~ 'autocommit': True
        #~ }
   #~ }
#~ }

# DEV
DATABASES = {
   'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'fixmystreet',
        'USER': 'fixmystreet',
        'PASSWORD': 'fms',
        'HOST': 'svappcavl158.dev.srv.cirb.lan',
        'PORT': 5432,
        #~ 'OPTIONS': {
            #~ 'autocommit': True
        #~ },
        'TEST_NAME': 'test_fixmystreet_afu'
   }
}

# STAGING
#~ DATABASES = {
   #~ 'default': {
        #~ 'ENGINE': 'django.contrib.gis.db.backends.postgis',
        #~ 'NAME': 'fixmystreet',
        #~ 'USER': 'fixmystreet',
        #~ 'PASSWORD': '7eCeya',
        #~ 'HOST': '192.168.13.164',
        #~ 'PORT': 5432,
        #~ 'OPTIONS': {
            #~ 'autocommit': True
        #~ }
   #~ }
#~ }

# !!!! PROD !!!!
#~ print '!!! DATABASE OF PRODUCTION !!!'
#~ print '!!! DATABASE OF PRODUCTION !!!'
#~ print '!!! DATABASE OF PRODUCTION !!!'
#~ DATABASES = {
   #~ 'default': {
        #~ 'ENGINE': 'django.contrib.gis.db.backends.postgis',
        #~ 'NAME': 'fixmystreet',
        #~ 'USER': 'fixmystreet',
        #~ 'PASSWORD': 'x0BLKa4HgR',
        #~ 'HOST': '192.168.15.177',
        #~ 'PORT': 5432,
        #~ 'OPTIONS': {
            #~ 'autocommit': True
        #~ }
   #~ }
#~ }

#~ EMAIL_BACKEND       = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/django-mail' # change this to a proper location

EMAIL_HOST          = "relay.irisnet.be"
EMAIL_ADMIN         = "afuca@cirb.irisnet.be"
#~ EMAIL_HOST_USER     = "django.dev@cirb.irisnet.be"
#~ EMAIL_HOST_PASSWORD = "Cirb2014"
ADMIN_EMAIL         = "afuca@cirb.irisnet.be"

FACEBOOK_API_SECRET         = '###'

GOOGLE_OAUTH2_CLIENT_ID     = '###'
GOOGLE_OAUTH2_CLIENT_SECRET = '###'

PDF_PRO_TOKEN_KEY='1234'
