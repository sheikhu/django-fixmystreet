from setuptools import setup

version = '0.1dev'

long_description = '\n\n'.join([
    open('README.md').read(),
    # open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'Django == 1.4.1',
    'django-transmeta',
    'django-stdimage',
    # 'django-social-auth',
    'south',
    'django-nose',
    'django-extensions',
    # 'lizard-ui >= 4.0b5'
    ],

deploy_require = [
    'gunicorn'
    ]
tests_require = [
    'django-jenkins',
    'coverage',
    'pylint'
    ]
debug_require = [
    'django-debug-toolbar',
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
    author='TODO',
    author_email='TODO@nelen-schuurmans.nl',
    url='',
    license='GPL',
    packages=['django_fixmystreet'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
      'deploy': deploy_require,
      'jenkins': tests_require,
      'debug': debug_require
      },
    entry_points={
        'console_scripts': []
        },
    )
