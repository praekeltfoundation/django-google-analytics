SECRET_KEY = 'foo'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',

    'google_analytics',
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

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
)

STATIC_URL = ''
SITE_ID = 1
GOOGLE_ANALYTICS = {
    'google_analytics_id': 'ua-test-id',
}
ROOT_URLCONF = 'google_analytics.urls'
