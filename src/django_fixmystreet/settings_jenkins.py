import os

from django_fixmystreet.settings import *

INSTALLED_APPS += ('django_jenkins',)

PROJECT_APPS = ('fixmystreet',)

JENKINS_TASKS = (
    'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.django_tests',
    #'django_jenkins.tasks.run_jslint',
)
