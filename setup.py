from setuptools import setup
import os

version = '2.3.4'

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

long_description = '\n\n'.join([
    open(os.path.join(PROJECT_PATH, 'README.md')).read(),
    # open('CREDITS.rst').read(),
    open(os.path.join(PROJECT_PATH, 'CHANGES.rst')).read(),
])

install_requires = [
    'django==1.5.5',
    'django-transmeta',
    'django-stdimage',
    'south==0.7.6',
    'django-extensions',
    'docutils',
    'markdown',
    'oauth2',
    'simplejson==1.9.3',
    'transifex-client',

    'django-extensions==1.0.1',
    'django-nose==1.1',
    'django-stdimage==0.2.2',
    'django-transmeta==0.6.9',

    'django-simple-history==1.3.0',
    'django-piston==0.2.3',
]

debug_require = [
    'django-debug-toolbar==0.9.4',
    'ipython',
    'zest.releaser==3.50',
    # 'django-pdb'
    # 'git+https://github.com/kmmbvnr/django-jenkins.git#egg=django-jenkins-1.5.0',
    'django-jenkins',
    'coverage==3.6',
    'flake8==2.1.0',
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
        'https://github.com/CIRB/django-simple-history/archive/3da627f01398fd88f812d789d21197cd622633a7.zip#egg=simple_history-1.1.3',
        'https://pypi.python.org/packages/source/d/django-piston/django-piston-0.2.3.tar.gz#md5=8b040d426793cf22ce89543e059cd6e1#egg=django-piston-0.2.3',
    ],
    extras_require={
        'debug': debug_require
    },
    entry_points={
        'console_scripts': []
    },
    scripts=['manage.py'],
)
