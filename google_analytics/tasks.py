import httplib2

from django.utils import timezone

from celery.task import task


@task(ignore_result=True)
def send_tracking(params, x_forwarded_for=None, timestamp=None):
    url = params.get('url')
    user_agent = params.get('user_agent')
    language = params.get('language')
    body = params.get('body')
    request_method = params.get('request_method')

    request_kwargs = {
        'headers': {
            'User-Agent': user_agent,
            'Accept-Language': language,
        }
    }
    if x_forwarded_for:
        request_kwargs['X-Forwarded-For'] = x_forwarded_for

    # if this is a UA event, add
    # the queue time parameter
    if timestamp and body:
        diff = timezone.now() - timestamp
        body = "%s&qt=%d" % (body, int(diff.total_seconds() * 1000))

    if request_method not in ('GET', 'HEAD') and body:
        request_kwargs['body'] = body

    # send the request
    http = httplib2.Http()
    try:
        resp, content = http.request(
            url, request_method,
            **request_kwargs
        )
    except httplib2.HttpLib2Error:
        raise Exception("Error opening: %s" % url)
