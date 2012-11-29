import shutil
import os

from django.core.files.storage import default_storage
from django.test import TestCase

class SampleFilesTestCase(TestCase):
    fixtures = ['sample']

    @classmethod
    def setUpClass(cls):
        shutil.copytree('media', 'media-tmp')
        default_storage.location = 'media-tmp'

    @classmethod
    def tearDownClass(self):
        shutil.rmtree('media-tmp')

    def _fixture_setup(self):
        if os.path.exists('media-tmp/photos'):
            shutil.rmtree('media-tmp/photos')
        shutil.copytree('media-tmp/photos-sample', 'media-tmp/photos')
        super(SampleFilesTestCase, self)._fixture_setup()

    def tearDown(self):
        shutil.rmtree('media-tmp/photos')

from django_fixmystreet.fixmystreet.tests.views import *
from django_fixmystreet.fixmystreet.tests.reports import *
from django_fixmystreet.fixmystreet.tests.users import *
from django_fixmystreet.fixmystreet.tests.organisation_entity import *
from django_fixmystreet.fixmystreet.tests.mail import *
# from django_fixmystreet.fixmystreet.tests.api import *
