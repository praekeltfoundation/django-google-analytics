MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django_ga',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

SECRET_KEY = 'foo'

ROOT_URLCONF = 'google_analytics.urls'

GOOGLE_ANALYTICS = {
    'ua_google_analytics_id': 'UA-00000000-01',
    'ga_google_analytics_id': 'UA-00000000-02',
    'CUSTOM_DATA_PROVIDERS': ('google_analytics.tests.custom_data', ),
}

INSTALLED_APPS = (
    'google_analytics',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sessions',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

STATIC_URL = ''
SITE_ID = 1
CELERY_ALWAYS_EAGER = True
