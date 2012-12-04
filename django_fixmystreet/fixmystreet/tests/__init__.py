import shutil
import os

from django.core.files.storage import default_storage
from django.test import TestCase

class SampleFilesTestCase(TestCase):
    fixtures = ['sample']

    @classmethod
    def setUpClass(cls):
        default_storage.location = 'media/' # force using source media folder to avoid real data erasing
    # @classmethod
    # def setUpClass(cls):
        # shutil.copytree('media', 'media-tmp')
        # default_storage.location = 'media-tmp'
# 
    # @classmethod
    # def tearDownClass(self):
        # shutil.rmtree('media-tmp')

    def _fixture_setup(self):
        if os.path.exists('media/photos'):
            shutil.rmtree('media/photos')
        shutil.copytree('media/photos-sample', 'media/photos')
        super(SampleFilesTestCase, self)._fixture_setup()


#from django_fixmystreet.fixmystreet.tests.views import *
#from django_fixmystreet.fixmystreet.tests.reports import *
#from django_fixmystreet.fixmystreet.tests.users import *
#from django_fixmystreet.fixmystreet.tests.organisation_entity import *
#from django_fixmystreet.fixmystreet.tests.mail import *
from django_fixmystreet.fixmystreet.tests.api import *
