from setuptools import setup
import os

version = '3.0.14'

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

long_description = '\n\n'.join([
    open(os.path.join(PROJECT_PATH, 'README.md')).read(),
    # open('CREDITS.rst').read(),
    open(os.path.join(PROJECT_PATH, 'CHANGES.rst')).read(),
])

install_requires = [
    'django==1.5.9',
    'django-transmeta',
    'django-stdimage',
    'south==0.7.6',
    'django-extensions',
    'docutils',
    'markdown',
    'simplejson==1.9.3',
    'transifex-client',

    'django-extensions==1.0.1',
    'django-stdimage==0.2.2',
    'django-transmeta==0.6.9',

    'django-simple-history==1.3.0',
    'django-piston==0.2.3',
    'django-ckeditor-updated==4.2.6',
    'gunicorn==18.0',
    'setproctitle==1.1.8',

    'mobileserverstatus'
]

dev_require = [
    'django-debug-toolbar==0.9.4',
    'ipython',
    'zest.releaser==3.50',
    # 'django-pdb'
    # 'git+https://github.com/kmmbvnr/django-jenkins.git#egg=django-jenkins-1.5.0',
    'django-jenkins==0.15.0',
    'coverage==3.6',
    'flake8==2.1.0',

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
        'https://github.com/riklaunim/django-ckeditor/archive/a3669f731145154efb7de52f79f1eb50ae4e54cf.zip#egg=django-ckeditor-updated-4.2.6',
        'https://github.com/cirb/mobileserverstatus/archive/1.0.zip#egg=mobileserverstatus',
    ],
    extras_require={
        'dev': dev_require
    },
    entry_points={
        'console_scripts': []
    },
    scripts=['manage.py'],
)
