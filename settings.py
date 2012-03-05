# Django settings for fixmystreet project.
import os, sys
import logging
import shutil

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

TEMPLATE_DIRS = (os.path.join(PROJECT_PATH, 'templates'),)
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

if hasattr(sys, 'argv') and sys.argv[1] == 'test':
    tmp_dir = os.path.join(PROJECT_PATH, 'media-tmp')
    
    try:
        shutil.rmtree(tmp_dir)
    except OSError:
        pass

    try:
        shutil.copytree(MEDIA_ROOT, tmp_dir)
    except OSError:
        pass

    MEDIA_ROOT = tmp_dir


MEDIA_URL = '/media/'

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
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

# include request object in template to determine active page
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.i18n',
    "django.contrib.messages.context_processors.messages",
    'social_auth.context_processors.social_auth_by_name_backends',
    'fixmystreet.utils.domain_context_processor'
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

ROOT_URLCONF = 'urls'

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
    'fixmystreet',
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
    'fixmystreet.googlebackend.GoogleProfileBackend',
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

DEBUG = False

#################################################################################
# These variables Should be defined in the local settings file
#################################################################################
#
#DATABASES = {
#   'default': {
#       'ENGINE': 'django.db.backends.postgresql',
#       'NAME': 'fixmystreet',
#       'USER': 'postgres',
#       'PASSWORD': 'xxx',
#       'HOST': 'localhost',
#       'PORT': 5432
#   }
#}
#EMAIL_USE_TLS =
#EMAIL_HOST =
#EMAIL_HOST_USER =
#EMAIL_HOST_PASSWORD =
#EMAIL_PORT =
#EMAIL_FROM_USER =

#LOCAL_DEV =
#SITE_URL = http://localhost:8000
#SECRET_KEY=
#GMAP_KEY=
#
#ADMIN_EMAIL =
#ADMINS =
#####################################################################################

# import local settings overriding the defaults
# local_settings.py is machine independent and should not be checked in

try:
    from local_settings import *
except ImportError:
    try:
        from mod_python import apache
        apache.log_error( "local_settings.py not set; using default settings", apache.APLOG_NOTICE )
    except ImportError:
        import sys
        sys.stderr.write( "local_settings.py not set; using default settings\n" )

TEMPLATE_DEBUG = True
