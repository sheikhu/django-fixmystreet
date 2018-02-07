from setuptools import setup, find_packages
import os

version = '4.1.0'

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

long_description = '\n\n'.join([
    open(os.path.join(PROJECT_PATH, 'README.md')).read(),
    # open('CREDITS.rst').read(),
    open(os.path.join(PROJECT_PATH, 'CHANGES.rst')).read(),
])

install_requires = [
    'django==1.8.18',

    'django-ckeditor==4.5.0',
    'django-extensions==1.5.9',
    'djangorestframework==3.1.3',
    'django-simple-history==1.6.2',
    'django-stdimage==2.3.2',
    'django-transmeta==0.7.3',
    #'django-status-monitoring',

    'python-dateutil==2.4.2',
    'python-logstash==0.4.5',

    'docutils==0.12',
    'gunicorn==18.0',
    'mobileserverstatus==1.0.2',
    'requests==2.7.0',
    'setproctitle==1.1.8', # Is it still used?
    'transifex-client==0.11.1.beta',
]

dev_require = [
    'django-debug-toolbar==1.3.2',
    'sqlparse==0.1.19', # force this version of sqlparse to get debug-toolbar working

    # These following packages depend on system requirements,
    # must be installed on system for prod
    'pillow==3.0.0',
    'psycopg2==2.6.1',

    # Jenkins
    'django-jenkins==0.17.0',
    'coverage==3.7.1',
    'flake8==2.4.1',
    'zest.releaser==3.50',
]

setup(
    name='django-fixmystreet',
    version=version,
    description="TODO",
    long_description=long_description,
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    keywords=[],
    author='CIRB',
    author_email='TODO@cirb.irisnet.be',
    url='',
    license='GPL',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    dependency_links=[
        'https://github.com/CIRB/mobileserverstatus/archive/1.0.2.zip#egg=mobileserverstatus-1.0.2'
        # 'http://stash.cirb.lan/plugins/servlet/archive/projects/DJANGO/repos/mobileserverstatus#egg=mobileserverstatus-1.0.2',
        # 'http://stash.cirb.lan/plugins/servlet/archive/projects/DJANGO/repos/django-status-monitoring?at=refs%2Fheads%2Fmaster#egg=django-status-monitoring'
    ],
    extras_require={
        'dev': dev_require
    },
    entry_points={
        'console_scripts': []
    },
    scripts=['manage.py'],
    )