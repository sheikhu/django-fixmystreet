from setuptools import setup, find_packages

setup(
    name = "django-fixmystreet",
    version = "0.9 beta",
    url = 'https://github.com/CIRB/django-fixmystreet',
    license = 'BSD',
    description = "",
    author = 'CIRB',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
    #extras_require = { 'test': ['django-debug-toolbar', 'django-jenkins'] }
)
