from django.test import TestCase

class FMSTestCase(TestCase):

    # Include initial_data due to regression in 1.0 <= South < 1.0.2
    # https://bitbucket.org/andrewgodwin/south/pull-request/157/fix-loading-initial_data-for-unit-tests/diff
    fixtures = ["initial_data", "bootstrap", "list_items"]

from django_fixmystreet.fixmystreet.tests.api import *
from django_fixmystreet.fixmystreet.tests.views import *
from django_fixmystreet.fixmystreet.tests.reports import *
from django_fixmystreet.fixmystreet.tests.dispatching import *
from django_fixmystreet.fixmystreet.tests.users import *
from django_fixmystreet.fixmystreet.tests.mail import *
from django_fixmystreet.fixmystreet.tests.history import *
from django_fixmystreet.fixmystreet.tests.export_pdf import *
from django_fixmystreet.fixmystreet.tests.reopen_request import *
