DATABASES = {
   'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'fixmystreet',
        'USER': '###',
        'PASSWORD': '###',
        'HOST': 'localhost',
        'PORT': 5432
   }
}

EMAIL_HOST = "relay.irisnet.be"
EMAIL_ADMIN = "###@cirb.irisnet.be"
ADMIN_EMAIL = "###@cirb.irisnet.be"

