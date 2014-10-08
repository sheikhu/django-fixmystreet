from django.core.files.storage import default_storage
from django.test import TestCase


class SampleFilesTestCase(TestCase):

    fixtures = ["bootstrap","list_items"]

    @classmethod
    def setUpClass(cls):
        default_storage.location = 'media/' # force using source media folder to avoid real data erasing

from django_fixmystreet.fixmystreet.tests.api import *
from django_fixmystreet.fixmystreet.tests.views import *
from django_fixmystreet.fixmystreet.tests.reports import *
from django_fixmystreet.fixmystreet.tests.dispatching import *
from django_fixmystreet.fixmystreet.tests.users import *
from django_fixmystreet.fixmystreet.tests.mail import *
from django_fixmystreet.fixmystreet.tests.history import *
from django_fixmystreet.fixmystreet.tests.export_pdf import *
