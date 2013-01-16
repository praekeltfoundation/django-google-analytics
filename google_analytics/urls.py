from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url(
        r'^google-analytics/$',
        'google_analytics.views.google_analytics',
        name='google-analytics'
    ),
)
