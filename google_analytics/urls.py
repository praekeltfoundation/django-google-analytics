from django.conf.urls import url

urlpatterns = [
    '',
    url(
        r'^google-analytics/$',
        'google_analytics.views.google_analytics',
        name='google-analytics'
    ),
]
