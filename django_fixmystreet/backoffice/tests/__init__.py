from django.test import TestCase

class FMSTestCase(TestCase):

    # Include initial_data due to regression in 1.0 <= South < 1.0.2
    # https://bitbucket.org/andrewgodwin/south/pull-request/157/fix-loading-initial_data-for-unit-tests/diff
    fixtures = ["initial_data", "bootstrap", "list_items"]

from django_fixmystreet.backoffice.tests.lists import *
from django_fixmystreet.backoffice.tests.updates import *
from django_fixmystreet.backoffice.tests.views import *
from django_fixmystreet.backoffice.tests.groups import *
from django_fixmystreet.backoffice.tests.users import *
from django_fixmystreet.backoffice.tests.dispatching import *
