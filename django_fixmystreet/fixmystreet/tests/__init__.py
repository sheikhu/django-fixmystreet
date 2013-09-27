

from django.core.files.storage import default_storage
from django.test import TestCase


class SampleFilesTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        default_storage.location = 'media/' # force using source media folder to avoid real data erasing

from django_fixmystreet.fixmystreet.tests.api import *
from django_fixmystreet.fixmystreet.tests.views import *
from django_fixmystreet.fixmystreet.tests.reports import *
from django_fixmystreet.fixmystreet.tests.users import *
from django_fixmystreet.fixmystreet.tests.organisation_entity import *
from django_fixmystreet.fixmystreet.tests.mail import *
from django_fixmystreet.fixmystreet.tests.history import *
from django_fixmystreet.fixmystreet.tests.export_pdf import *

# class TestDiscoveryPlugin(Plugin):
#     enabled = True

#     def configure(self, options, conf):
#         super(TestDiscoveryPlugin, self).configure(options, conf)
#         self.enabled = True

#     def wantDirectory(self, dirname):
#         parts = dirname.split(os.path.sep)
#         print parts
#         return 'tests' in parts

#     def wantClass(self, cls):
#         return issubclass(cls, TestCase)

#     def wantFile(self, filename):
#         parts = filename.split(os.path.sep)
#         return 'tests' in parts and filename.endswith('.py')

#     def wantModule(self, module):
#         parts = module.__name__.split('.')
#         return 'tests' in parts
