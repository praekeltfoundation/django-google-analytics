import codecs
import os

from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), 'rb', 'utf-8') as f:
        return f.read()


setup(
    name='django-google-analytics-app',
    version='4.2.0',
    description=('Django Google Analytics app allowing for server side/non-js '
                 'tracking.'),
    long_description=read('README.rst'),
    author='Praekelt Foundation',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://github.com/praekelt/django-google-analytics',
    packages=find_packages(),
    install_requires=[
        'django<2.0',
        'django-celery',
        'celery<4.0',
        'requests',
        'beautifulsoup4',
        'six>=1.11.0,<2.0',
    ],
    include_package_data=True,
    tests_require=[
        'django-setuptest',
    ],
    test_suite="setuptest.setuptest.SetupTestSuite",
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)
