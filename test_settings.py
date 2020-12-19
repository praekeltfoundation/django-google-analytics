import os

SECRET_KEY = 'foo'
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'google_analytics',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')],
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'molo.core.context_processors.locale',
            'molo.core.processors.compress_settings',
            'wagtail.contrib.settings.context_processors.settings',
        ],
    },
}]

STATIC_URL = ''
SITE_ID = 1
GOOGLE_ANALYTICS = {
    'google_analytics_id': 'ua-test-id',
}
ROOT_URLCONF = 'google_analytics.urls'

CUSTOM_UIP_HEADER = 'HTTP_X_IORG_FBS_UIP'

TEST_RUNNER = 'google_analytics.test_runner.CeleryTestSuiteRunner'

CELERY_ALWAYS_EAGER = True
