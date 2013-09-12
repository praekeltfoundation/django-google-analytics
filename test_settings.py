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

GOOGLE_ANALYTICS = {
    'google_analytics_id': '',
}

ROOT_URLCONF = 'google_analytics.urls'

GOOGLE_ANALYTICS = {
    'google_analytics_id': 'UA-00000000-00',
}

INSTALL_APPS = (
    'google_analytics',
)