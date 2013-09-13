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

SECRET_KEY = 'x'

ROOT_URLCONF = 'google_analytics.urls'

GOOGLE_ANALYTICS = {
    'google_analytics_id': 'UA-00000000-00',
    'CUSTOM_DATA_PROVIDERS': ('tests.custom_dimensions', ),
}

INSTALLED_APPS = (
    'google_analytics',
    'django.contrib.sessions',
)
