import httplib2
from celery.task import task


@task(ignore_result=True)
def send_ga_tracking(params):
    utm_url = params.get('utm_url')
    user_agent = params.get('user_agent')
    language = params.get('language')

    # send the request
    http = httplib2.Http()
    try:
        resp, content = http.request(
            utm_url, 'GET',
            headers={
                'User-Agent': user_agent,
                'Accepts-Language:': language
            }
        )
    except httplib2.HttpLib2Error:
        raise Exception("Error opening: %s" % utm_url)
