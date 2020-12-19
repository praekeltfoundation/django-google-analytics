import requests

from celery import task


@task(ignore_result=True)
def send_ga_tracking(params):
    utm_url = params.get('utm_url')
    user_agent = params.get('user_agent')
    language = params.get('language')

    headers = {'User-Agent': user_agent, 'Accepts-Language': language}
    requests.get(utm_url, headers=headers)
