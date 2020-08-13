import re
import struct
from functools import reduce

import requests

from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from google_analytics.utils import build_ga_params, set_cookie

GIF_DATA = reduce(lambda x, y: x + struct.pack('B', y),
                  [0x47, 0x49, 0x46, 0x38, 0x39, 0x61,
                   0x01, 0x00, 0x01, 0x00, 0x80, 0x00,
                   0x00, 0x00, 0x00, 0x00, 0xff, 0xff,
                   0xff, 0x21, 0xf9, 0x04, 0x01, 0x00,
                   0x00, 0x00, 0x00, 0x2c, 0x00, 0x00,
                   0x00, 0x00, 0x01, 0x00, 0x01, 0x00,
                   0x00, 0x02, 0x01, 0x44, 0x00, 0x3b], b'')


def get_ip(remote_address):
    if not remote_address:
        return ''
    matches = re.match(r'^([^.]+\.[^.]+\.[^.]+\.).*', remote_address)
    if matches:
        return matches.groups()[0] + "0"
    else:
        return ''


def google_analytics_request(request, response, path=None, event=None):
    # get the account id
    account = request.GET.get('tracking_code')

    params = build_ga_params(request, account, event=event)

    set_cookie(params, response)

    utm_url = params.get('utm_url')
    user_agent = params.get('user_agent')
    language = params.get('language')

    # send the request
    resp = requests.get(
        utm_url,
        headers={
            'User-Agent': user_agent,
            'Accepts-Language': language
        }
    )
    # send debug headers if debug mode is set
    if request.GET.get('utmdebug', False):
        response['X-GA-MOBILE-URL'] = utm_url
        response['X-GA-RESPONSE'] = resp

    # return the augmented response
    return response


@never_cache
def google_analytics(request):
    """Image that sends data to Google Analytics."""
    event = request.GET.get('event', None)
    if event:
        event = event.split(',')
    response = HttpResponse('', 'image/gif', 200)
    response.write(GIF_DATA)
    return google_analytics_request(request, response, event=event)
