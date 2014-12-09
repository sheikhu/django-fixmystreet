from setuptools import setup
import os

version = '3.0.37'

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

long_description = '\n\n'.join([
    open(os.path.join(PROJECT_PATH, 'README.md')).read(),
    # open('CREDITS.rst').read(),
    open(os.path.join(PROJECT_PATH, 'CHANGES.rst')).read(),
])

install_requires = [
    'django==1.5.11',
    'django-transmeta==0.6.9',
    'django-stdimage==0.2.2',
    'south==1.0.1',
    'django-extensions==1.0.1',
    'docutils==0.11',
    'simplejson==1.9.3',
    'transifex-client==0.11.1.beta',

    'django-extensions==1.0.1',
    'django-stdimage==0.2.2',
    'django-transmeta==0.6.9',

    'django-simple-history==1.3.0',
    'django-piston==0.2.3',
    'gunicorn==18.0',
    'setproctitle==1.1.8',

    'mobileserverstatus==1.0',

    'requests==2.4.3',
    'djangorestframework==2.4.4',
    'python-dateutil==1.5',
    'django-ckeditor==4.4.6',
]

dev_require = [
    'django-debug-toolbar==0.9.4',
    'ipython',
    'zest.releaser==3.50',
    # 'django-pdb'
    # 'git+https://github.com/kmmbvnr/django-jenkins.git#egg=django-jenkins-1.5.0',
    'django-jenkins==0.15.0',
    'coverage',
    'flake8',

    # this following package depend on system requirements,
    # must be installed on system for prod
    'pillow',
    'psycopg2'
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
    packages=['django_fixmystreet'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    dependency_links=[
        'https://pypi.python.org/packages/source/d/django-piston/django-piston-0.2.3.tar.gz#md5=8b040d426793cf22ce89543e059cd6e1#egg=django-piston-0.2.3',
        'https://github.com/cirb/mobileserverstatus/archive/1.0.zip#egg=mobileserverstatus-1.0',
        'http://trac.transifex.org/files/deps/django-piston-0.2.3.tar.gz#egg=piston'
    ],
    extras_require={
        'dev': dev_require
    },
    entry_points={
        'console_scripts': []
    },
    scripts=['manage.py'],
)
