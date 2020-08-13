from django.conf.urls import url
from google_analytics.views import google_analytics

urlpatterns = [
    url(r'^google-analytics/$', google_analytics, name='google-analytics'),
]
