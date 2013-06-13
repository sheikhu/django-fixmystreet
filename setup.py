from setuptools import setup
import os

version = '1.1.9'

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

long_description = '\n\n'.join([
    open(os.path.join(PROJECT_PATH, 'README.md')).read(),
    # open('CREDITS.rst').read(),
    open(os.path.join(PROJECT_PATH, 'CHANGES.rst')).read(),
    ])

install_requires = [
    'django',
    'django-transmeta',
    'django-stdimage',
    'south',
    'django-extensions',
    'simple_history',
    'docutils',
    # 'django-registration',
    'django-piston',
    'markdown',
    'oauth2',
    'simplejson'
    ]

tests_require = [
    'django-jenkins',
    'coverage',
    'pyflakes'
    ]

debug_require = [
    'django-debug-toolbar',
    'ipython',
    # 'django-pdb'
    ]

setup(name='django-fixmystreet',
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
    tests_require=tests_require,
    extras_require={
      'jenkins': tests_require,
      'debug': debug_require
      },
    entry_points={
        'console_scripts': []
        },
    )
