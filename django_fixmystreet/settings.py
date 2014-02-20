# Django settings for fixmystreet project.
import os
import sys
import subprocess

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.getcwd()

# supported value of ENVIRONMENT are dev, jenkins, staging, production
if "ENV" in os.environ:
    ENVIRONMENT = os.environ['ENV']
else:
    ENVIRONMENT = "local"

if ENVIRONMENT == "local" or ENVIRONMENT == "dev" or ENVIRONMENT == "jenkins":
    DEBUG = True
else:
    DEBUG = False

if ENVIRONMENT != "production":
    #disable mail in non-production environment
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


LOGIN_REQUIRED_URL = '^/(.*)/pro/'

LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'fr')
GA_CODE = os.environ.get('GA_CODE', '')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
ADMINS = (('Django Dev Team', 'django.dev@cirb.irisnet.be'),)
SERVER_EMAIL = "fixmystreet@cirb.irisnet.be"

EMAIL_SUBJECT_PREFIX = "[DJA-{0}] ".format(ENVIRONMENT[0:4])

MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))
REPORTING_ROOT = os.environ.get('REPORTING_ROOT', os.path.join(BASE_DIR, 'reporting'))

# CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_ROOT, 'uploads')
CKEDITOR_UPLOAD_PATH = MEDIA_ROOT


STATIC_ROOT = os.path.join(BASE_DIR, 'static')

LOCALE_PATHS = (os.path.join(PROJECT_PATH, 'django_fixmystreet', 'locale'),)

DEFAULT_FROM_EMAIL = "Fix My Street<noreply@fixmystreet.irisnet.be>"

MEDIA_URL = '/media/'
STATIC_URL = '/static/'

POSTGIS_TEMPLATE = 'template_postgis'

PROXY_URL = "http://gis.irisnet.be/"
URBIS_URL = "/urbis/"

TIME_ZONE = 'Europe/Brussels'

FILE_UPLOAD_PERMISSIONS = 0644
DATE_FORMAT = "d-m-Y H:i"
DATETIME_FORMAT = "d-m-Y H:i"

# Max file upload size
#MAX_UPLOAD_SIZE = "821440"
MAX_UPLOAD_SIZE = "15000000"

#Max number of items per pagination
MAX_ITEMS_PAGE = 10

USE_I18N = True
REGISTRATION_OPEN = False
ROOT_URLCONF = 'django_fixmystreet.urls'
# AUTH_PROFILE_MODULE = "django_fixmystreet.fixmystreet.FMSUser"
# AUTH_USER_MODEL = "django_fixmystreet.fixmystreet.FMSUser"

SOUTH_LOGGING_ON = True
SOUTH_LOGGING_FILE = os.path.join(BASE_DIR, "south.log")
CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/.*'


if ENVIRONMENT == "local":
    proc = subprocess.Popen('{0} {1}/setup.py --version'.format(sys.executable, PROJECT_PATH), stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    VERSION = out
else:
    import pkg_resources
    VERSION = pkg_resources.require("django-fixmystreet")[0].version

gettext = lambda s: s
LANGUAGES = (
    # ('en', gettext('English')),
    ('fr', gettext('French')),
    ('nl', gettext('Dutch')),
)

TEMPLATE_DIRS = (
    "/home/jsanchezpando/Projects/django-fixmystreet/env/lib/python2.7/site-packages/django_simple_history-1.3.0-py2.7.egg/simple_history/templates/",
)

# include request object in template to determine active page
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.i18n',
    'django.contrib.auth.context_processors.auth',
    "django.contrib.messages.context_processors.messages",
    'django_fixmystreet.fixmystreet.context_processor.domain',
    'django_fixmystreet.fixmystreet.context_processor.environment',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django_fixmystreet.backoffice.middleware.LoginRequiredMiddleware',
    'django_fixmystreet.backoffice.middleware.LoadUserMiddleware',
    'django_fixmystreet.fixmystreet.utils.CurrentUserMiddleware',
    'django_fixmystreet.fixmystreet.utils.CorsMiddleware',
    # 'django_fixmystreet.fixmystreet.utils.AccessControlAllowOriginMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.gis',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    'django.contrib.sitemaps',

    'transmeta',
    'south',
    'simple_history',
    'django_extensions',
    'ckeditor',
    'django_fixmystreet.fixmystreet',
    'django_fixmystreet.backoffice',
    'django_fixmystreet.monitoring',
    'piston',
)

# AUTHENTICATION_BACKENDS = (
#     'django.contrib.auth.backends.ModelBackend',
# )


if ENVIRONMENT != 'local':
    INSTALLED_APPS += ('gunicorn', )
else:
    try:
        __import__('debug_toolbar')
        INSTALLED_APPS += ('debug_toolbar', )
        MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

        # INSTALLED_APPS += ('django_pdb', )
        # MIDDLEWARE_CLASSES += ('django_pdb.middleware.PdbMiddleware',)

        __import__('django_jenkins')
        INSTALLED_APPS += ('django_jenkins',)
        PROJECT_APPS = ('fixmystreet',)
        JENKINS_TASKS = (
            # 'django_jenkins.tasks.run_flake8',
            'django_jenkins.tasks.with_coverage',
            'django_jenkins.tasks.django_tests',
        )
    except ImportError, e:
        print "WARNING: running `make install` in local?"
        print e

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'django_fixmystreet': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

if ENVIRONMENT == "local" or ENVIRONMENT == "dev" or ENVIRONMENT == "jenkins":
    SITE_ID = 3
    ALLOWED_HOSTS = ("*", )
    EMAIL_HOST = "localhost"

elif ENVIRONMENT == "staging":
    SITE_ID = 2
    ALLOWED_HOSTS = ("fixmystreet.irisnetlab.be", )

elif ENVIRONMENT == "production":
    SITE_ID = 1
    ALLOWED_HOSTS = ("fixmystreet.irisnet.be", )


try:
    from local_settings import * # flake8: noqa
except ImportError:
    pass
if not 'DATABASES' in locals():
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

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'fms_cache',
    },
    'staticfiles': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'
