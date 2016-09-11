SECRET_KEY = 'foo'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',

    'djcelery',
    'google_analytics',
    'django.contrib.sessions',
    'kombu.transport.django',
]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
]

STATIC_URL = ''
SITE_ID = 1
GOOGLE_ANALYTICS = {
    'google_analytics_id': 'ua-test-id',
}
ROOT_URLCONF = 'google_analytics.urls'

CUSTOM_UIP_HEADER = 'HTTP_X_IORG_FBS_UIP'

CELERY_RESULT_BACKEND = BROKER_URL = 'django://'
CELERY_ALWAYS_EAGER = True
TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
