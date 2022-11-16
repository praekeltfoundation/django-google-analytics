import codecs
import os

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), 'rb', 'utf-8') as f:
        return f.read()


setup(
    name='django-google-analytics-app',
    version='6.0.0',
    description=('Django Google Analytics app allowing for server side/non-js '
                 'tracking.'),
    long_description=read('README.rst'),
    author='Praekelt.org',
    author_email='dev@praekelt.org',
    license='BSD',
    url='http://github.com/praekelt/django-google-analytics',
    packages=find_packages(),
    install_requires=[
        'Django>=3.2,<4.2',
        # https://github.com/celery/celery/issues/7783
        "importlib_metadata<5; python_version=='3.7'",
        'celery<5.2.3',
        'requests',
        'beautifulsoup4',
        'structlog',
    ],
    extras_require={
        'test': ['responses'],
        'lint': ['flake8'],
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords=['django', 'google', 'analytics'],
    zip_safe=False,
)
