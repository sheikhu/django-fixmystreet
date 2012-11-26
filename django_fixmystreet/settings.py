# Django settings for fixmystreet project.
import os, sys
import logging

PROJECT_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

LOGIN_REQUIRED_URLS = '^pro/'

if 'MEDIA_ROOT' in os.environ:
    MEDIA_ROOT = os.environ['MEDIA_ROOT']
else:
    MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')

MEDIA_URL = '/media/'
STATIC_URL = '/static/'

POSTGIS_TEMPLATE = 'template_postgis'

TIME_ZONE = 'Europe/Brussels'

FILE_UPLOAD_PERMISSIONS = 0644
DATE_FORMAT = "l, j F Y"

#Max file upload size
MAX_UPLOAD_SIZE = "821440"


# include request object in template to determine active page
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.i18n',
    'django.contrib.auth.context_processors.auth',
    "django.contrib.messages.context_processors.messages",
    'django_fixmystreet.fixmystreet.context_processor.domain',
    'django_fixmystreet.fixmystreet.context_processor.environment'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django_fixmystreet.backoffice.middleware.LoginRequiredMiddleware',
    'django_fixmystreet.backoffice.middleware.LoadUserMiddleware'
)

LANGUAGE_CODE = os.environ['LANGUAGE_CODE'] if 'LANGUAGE_CODE' in os.environ else 'fr'
USE_I18N = True

gettext = lambda s: s
LANGUAGES = (
  ('en', gettext('English')),
  ('fr', gettext('French')),
  ('nl', gettext('Dutch')),
)

ROOT_URLCONF = 'django_fixmystreet.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.gis',
    
    'transmeta',
    'south',
    'django_extensions',
    'django_fixmystreet.fixmystreet',
    'django_fixmystreet.backoffice',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

ADD_THIS_KEY = os.environ['ADD_THIS_KEY'] if 'ADD_THIS_KEY' in os.environ else 'Not set'

EMAIL_FROM_USER = "Fix My Street<fixmystreet@cirb.irisnet.be>"
DEFAULT_FROM_EMAIL = "Fix My Street<fixmystreet@cirb.irisnset.be>"


# supported value of ENVIRONMENT are dev, jenkins, staging, production
if "ENV" in os.environ:
    ENVIRONMENT = os.environ['ENV']
else:
    ENVIRONMENT = "local"
    sys.stderr.write( "No ENV specified, using local.\n" ) 



try:
    __import__('gunicorn')
    print "using gunicorn"
    INSTALLED_APPS += ('gunicorn', )
except ImportError:
    pass

try:
    __import__('debug_toolbar')
    print "using debug toolbar"
    INSTALLED_APPS += ('debug_toolbar', )
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    INTERNAL_IPS = ('127.0.0.1',)
except ImportError:
    pass

try:
    __import__('django_jenkins')
    INSTALLED_APPS += ('django_jenkins',)
    PROJECT_APPS = ('fixmystreet',)
    JENKINS_TASKS = (
        'django_jenkins.tasks.with_coverage',
        'django_jenkins.tasks.django_tests',
    )
except ImportError:
    pass



if ENVIRONMENT=="local" or ENVIRONMENT=="jenkins" or ENVIRONMENT=="dev" or ENVIRONMENT=="staging":
    DEBUG = True
    GEOSERVER = "geoserver.gis.irisnetlab.be"
    SERVICE_GIS = "service.gis.irisnetlab.be"
else:
    DEBUG = False
    GEOSERVER = "geoserver.gis.irisnet.be"
    SERVICE_GIS = "service.gis.irisnet.be"

if ENVIRONMENT=="local":
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(levelname)s %(message)s',
        filename = os.path.join(PROJECT_PATH, 'fixmystreet.log'),
        filemode = 'w'
    )

if ENVIRONMENT=="dev" or ENVIRONMENT=="local" or ENVIRONMENT=="jenkins":
    SITE_ID = 3

elif ENVIRONMENT=="staging":
    SITE_ID = 2
    SITE_URL = "fixmystreet.irisnetlab.be"

elif ENVIRONMENT=="production":
    SITE_ID = 1
    SITE_URL = "fixmystreet.irisnet.be"


try:
    from local_settings import *
except ImportError:
    import sys
    sys.stderr.write( "local_settings.py not set; using environment settings\n" )
    DATABASES = {
       'default': {
            'ENGINE': os.environ['DATABASE_ENGINE'],
            'NAME': os.environ['DATABASE_NAME'],
            'USER': os.environ['DATABASE_USER'],
            'PASSWORD': os.environ['DATABASE_PASSWORD'],
            'HOST': os.environ['DATABASE_HOST'],
            'PORT': os.environ['DATABASE_PORT'],
            'OPTIONS': {
                'autocommit': True
            }
       }
    }
    if 'EMAIL_ADMIN' in os.environ:
        EMAIL_ADMIN = os.environ['EMAIL_ADMIN']
    else:
        EMAIL_ADMIN = 'jsanchezpando@cirb.irisnet.be'
    ADMIN_EMAIL = EMAIL_ADMIN

