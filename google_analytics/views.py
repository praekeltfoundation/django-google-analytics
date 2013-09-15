import httplib2
import re
import struct
from sre_constants import error as sre_error

from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from google_analytics.utils import (build_params, set_cookie, heal_headers)


GIF_DATA = reduce(lambda x, y: x + struct.pack('B', y),
                  [0x47, 0x49, 0x46, 0x38, 0x39, 0x61,
                   0x01, 0x00, 0x01, 0x00, 0x80, 0x00,
                   0x00, 0x00, 0x00, 0x00, 0xff, 0xff,
                   0xff, 0x21, 0xf9, 0x04, 0x01, 0x00,
                   0x00, 0x00, 0x00, 0x2c, 0x00, 0x00,
                   0x00, 0x00, 0x01, 0x00, 0x01, 0x00,
                   0x00, 0x02, 0x01, 0x44, 0x00, 0x3b], '')


def get_ip(remote_address):
    if not remote_address:
        return ''
    matches = re.match('^([^.]+\.[^.]+\.[^.]+\.).*', remote_address)
    if matches:
        return matches.groups()[0] + "0"
    else:
        return ''


def google_analytics_request(request, response, path=None, event=None):
    params = build_params(request, event=event)

    set_cookie(params, response)

    url = params.get('url')
    user_agent = params.get('user_agent')
    language = params.get('language')
    body = params.get('body')
    request_method = params.get('request_method')

    request_kwargs = {
        'headers': {
            'User-Agent': user_agent,
        }
    }
    if language:
        request_kwargs['headers']['Accept-Language'] = language
    if request.META.get('HTTP_X_FORWARDED_FOR', ''):
        request_kwargs['headers']['X-Forwarded-For'] = \
            request.META.get('HTTP_X_FORWARDED_FOR')

    if request_method not in ('GET', 'HEAD') and body:
        request_kwargs['body'] = body

    # send the request
    http = httplib2.Http()
    try:
        try:
            resp, content = http.request(
                url, request_method,
                **request_kwargs
            )
        except sre_error:
            heal_headers(request_kwargs['headers'])
            resp, content = http.request(
                url, request_method,
                **request_kwargs
            )
        # send debug headers if debug mode is set
        if request.GET.get('gadebug', False):
            response['X-GA-MOBILE-URL'] = url
            response['X-GA-RESPONSE'] = resp

        # return the augmented response
        return response
    except httplib2.HttpLib2Error:
        raise Exception("Error opening: %s" % url)


@never_cache
def google_analytics(request):
    """Image that sends data to Google Analytics."""
    event = request.GET.get('event', None)
    if event:
        event = event.split(',')
    response = HttpResponse('', 'image/gif', 200)
    response.write(GIF_DATA)
    return google_analytics_request(request, response, event=event)
