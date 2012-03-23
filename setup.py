from setuptools import setup, find_packages

version = "0.9 beta"

setup(
    name = "django-fixmystreet",
    version = version,
    url = 'https://github.com/CIRB/django-fixmystreet',
    license = 'BSD',
    description = "",
    author = 'CIRB',
    packages=find_packages(exclude=['ez_setup']),
    #package_dir = {'': 'src'},
    install_requires = ['setuptools', 
                        'django',],
    #extras_require = { 'test': ['django-debug-toolbar', 'django-jenkins'] }
    entry_points="""
    # -*- Entry points: -*-
    """,
)
