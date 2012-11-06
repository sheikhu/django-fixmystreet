# Django settings for fixmystreet project.
import os, sys
import logging
import shutil

PROJECT_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

# TEMPLATE_DIRS = (os.path.join(PROJECT_PATH, 'templates'),)
if 'MEDIA_ROOT' in os.environ:
    MEDIA_ROOT = os.environ['MEDIA_ROOT']
else:
    MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')

MEDIA_URL = '/media/'
STATIC_URL = '/static/'

#TEST_RUNNER = 'django.contrib.gis.tests.run_tests'
POSTGIS_TEMPLATE = 'template_postgis'

logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
    filename = '/tmp/fixmystreet.log',
    filemode = 'w'
)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# ensure large uploaded files end up with correct permissions.  See
# http://docs.djangoproject.com/en/dev/ref/settings/#file-upload-permissions

FILE_UPLOAD_PERMISSIONS = 0644
DATE_FORMAT = "l, j F Y"

# List of callables that know how to import templates from various sources.
# TEMPLATE_LOADERS = (
    # 'django.template.loaders.filesystem.Loader',
    # 'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.load_template_source',
# )

# include request object in template to determine active page
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.i18n',
    'django.contrib.auth.context_processors.auth',
    "django.contrib.messages.context_processors.messages",
    'social_auth.context_processors.social_auth_by_name_backends',
    'django_fixmystreet.fixmystreet.utils.domain_context_processor'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = os.environ['LANGUAGE_CODE'] if 'LANGUAGE_CODE' in os.environ else 'fr'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
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
    'social_auth',
    'south',
    'django_fixmystreet.fixmystreet',
)

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuthBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.google.GoogleBackend',
    'social_auth.backends.yahoo.YahooBackend',
    'social_auth.backends.contrib.linkedin.LinkedinBackend',
    'social_auth.backends.contrib.livejournal.LiveJournalBackend',
    'social_auth.backends.contrib.orkut.OrkutBackend',
    'social_auth.backends.contrib.foursquare.FoursquareBackend',
    'social_auth.backends.contrib.github.GithubBackend',
    'social_auth.backends.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
    'django_fixmystreet.fixmystreet.googlebackend.GoogleProfileBackend',
)

SOCIAL_AUTH_ENABLED_BACKENDS = ('google-profile', 'facebook')

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/login-callback/'

FACEBOOK_EXTENDED_PERMISSIONS = ('email',)

#for client secret see local settings
FACEBOOK_APP_ID             = '263584440367959'
GOOGLE_OAUTH2_CLIENT_ID     = '985105651100.apps.googleusercontent.com'


LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL    = '/'


ADD_THIS_KEY = "broken" #"xa-4a620b09451f9502"

EMAIL_FROM_USER = "Fix My Street<fixmystreet@cirb.irisnet.be>"
DEFAULT_FROM_EMAIL = "Fix My Street<fixmystreet@cirb.irisnset.be>"


if "ENV" in os.environ:
    # supported value of ENVIRONMENT are dev, jenkins, staging, production
    ENVIRONMENT = os.environ['ENV']
else:
    ENVIRONMENT = "dev"
    sys.stderr.write( "No ENV specified, using dev.\n" ) 



if ENVIRONMENT=="dev" or ENVIRONMENT=="jenkins" or ENVIRONMENT=="staging":
    DEBUG = True
    GEOSERVER = "geoserver.gis.irisnetlab.be"
    SERVICE_GIS = "service.gis.irisnetlab.be"
else:
    DEBUG = False
    GEOSERVER = "geoserver.gis.irisnet.be"
    SERVICE_GIS = "service.gis.irisnet.be"



if ENVIRONMENT=="dev":
    SITE_ID = 3
    # INSTALLED_APPS += ('debug_toolbar', )
    # MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

elif ENVIRONMENT=="jenkins":
    SITE_ID = 3
    INSTALLED_APPS += ('django_jenkins',)
    PROJECT_APPS = ('fixmystreet',)
    JENKINS_TASKS = (
        'django_jenkins.tasks.run_pylint',
        'django_jenkins.tasks.with_coverage',
        'django_jenkins.tasks.django_tests',
        #'django_jenkins.tasks.run_jslint',
    )

elif ENVIRONMENT=="staging":
    SITE_ID = 2
    SITE_URL = "fixmystreet.irisnetlab.be"

elif ENVIRONMENT=="production":
    SITE_ID = 1
    SITE_URL = "fixmystreet.irisnet.be"

JSLINT_CHECKED_FILES = (
    'media/js/fixmystreetmap.js'
)

PYLINT_RCFILE = os.path.join(PROJECT_PATH, 'pylintrc')


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
    EMAIL_ADMIN = os.environ['EMAIL_ADMIN']
    ADMIN_EMAIL = os.environ['EMAIL_ADMIN']

