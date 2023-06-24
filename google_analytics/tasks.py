import requests

from django.conf import settings
from celery import shared_task


@shared_task(ignore_result=True)
def send_ga_tracking(params):
    try:
        account = settings.GOOGLE_ANALYTICS['google_analytics_id']
    except (KeyError, TypeError):
        raise Exception("No Google Analytics ID configured")
    try:
        api_secret = settings.GOOGLE_ANALYTICS['google_analytics_mp_api_secret']
    except (KeyError, TypeError):
        raise Exception("No Google Analytics MP API Secret configured")

    url = f"https://www.google-analytics.com/mp/collect?measurement_id={account}&api_secret={api_secret}"

    utm_url = params.get('utm_url')
    user_agent = params.get('user_agent')
    language = params.get('language')
    visitor_id = params.get('visitor_id')

    headers = {'User-Agent': user_agent, 'Accepts-Language': language}
    requests.post(url=url, headers=headers, data={
        "client_id": visitor_id,
        "events": [{
            "name": "page_view",
            "params": {"session_id":"123", "engagement_time_msec": "100"}
        }]
    })
