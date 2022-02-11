from django.urls import path
from google_analytics.views import google_analytics

urlpatterns = [
    path('google-analytics/', google_analytics, name='google-analytics'),
]
