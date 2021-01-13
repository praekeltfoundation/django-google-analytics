import random
import time
import uuid

from six import text_type
from six.moves.urllib.parse import quote, urlencode

import structlog
from django.conf import settings
from django.utils.translation import get_language_from_request
from google_analytics import CAMPAIGN_TRACKING_PARAMS

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

VERSION = '1'
COOKIE_NAME = '__utmmobile'
COOKIE_PATH = '/'
COOKIE_USER_PERSISTENCE = 63072000
CAMPAIGN_PARAMS_KEY = 'ga_campaign_params'


def get_visitor_id(guid, cookie):
    """Generate a visitor id for this hit.
    If there is a visitor id in the cookie, use that, otherwise
    use the guid if we have one, otherwise use a random number.
    """
    if cookie:
        return cookie
    if guid:
        # create the visitor id using the guid.
        cid = guid
    else:
        # otherwise this is a new user, create a new random id.
        cid = str(uuid.uuid4())
    return cid


def set_cookie(params, response):
    COOKIE_USER_PERSISTENCE = params.get('COOKIE_USER_PERSISTENCE')
    COOKIE_PATH = params.get('COOKIE_PATH')
    visitor_id = params.get('visitor_id')

    time_tup = time.localtime(time.time() + COOKIE_USER_PERSISTENCE)

    # always try and add the cookie to the response
    response.set_cookie(
        COOKIE_NAME,
        value=visitor_id,
        expires=time.strftime('%a, %d-%b-%Y %H:%M:%S %Z', time_tup),
        path=COOKIE_PATH,
    )
    return response


def build_ga_params(
        request, account, path=None, event=None, referer=None, title=None,
        user_id=None, custom_params={}):
    meta = request.META
    # determine the domian
    domain = meta.get('HTTP_HOST', '')
    ni = '0' if request.method == 'GET' else '1'
    # determine the referrer
    referer = referer or request.GET.get('r', '')
    parse_referer = urlparse(referer)
    if parse_referer.netloc == domain:
        referer = parse_referer.path

    custom_uip = None
    if hasattr(settings, 'CUSTOM_UIP_HEADER') and settings.CUSTOM_UIP_HEADER:
        custom_uip = meta.get(settings.CUSTOM_UIP_HEADER)
    # get the path from the referer header
    path = path or request.GET.get('p', '/')

    # try and get visitor cookie from the request
    user_agent = meta.get('HTTP_USER_AGENT', 'Unknown')
    cookie = request.COOKIES.get(COOKIE_NAME)
    visitor_id = get_visitor_id(meta.get('HTTP_X_DCMGUID', ''), cookie)

    # get client ip address
    if 'HTTP_X_FORWARDED_FOR' in meta and meta.get('HTTP_X_FORWARDED_FOR', ''):
        client_ip = meta.get('HTTP_X_FORWARDED_FOR', '')
        if client_ip:
            # The values in a proxied environment are usually presented in the
            # following format:
            # X-Forwarded-For: client, proxy1, proxy2
            # In this case, we want the client IP Only
            client_ip = client_ip.split(',')[0]
    else:
        client_ip = meta.get('REMOTE_ADDR', '')

    # build the parameter collection
    params = {
        'v': VERSION,
        'z': str(random.randint(0, 0x7fffffff)),
        'dh': domain,
        'sr': '',
        'dr': referer,
        'dp': quote(path.encode('utf-8')),
        'tid': account,
        'cid': visitor_id,
        'uip': custom_uip or client_ip,
        'ni': ni,
    }

    # add user ID if exists
    if user_id:
        params.update({'uid': user_id})

    # add custom parameters
    params.update(custom_params)

    # add page title if supplied
    if title:
        u_title = title.decode('utf-8') if isinstance(title, bytes) else title
        params.update({'dt': quote(text_type(u_title).encode('utf-8'))})
    # add event parameters if supplied
    if event:
        params.update({
            't': 'event',
            'utme': '5(%s)' % '*'.join(event),
        })
    else:
        params.update({'t': 'pageview'})

    # retrieve campaign tracking parameters from session
    campaign_params = request.session.get(CAMPAIGN_PARAMS_KEY, {})

    # update campaign params from request
    for param in CAMPAIGN_TRACKING_PARAMS:
        ga_name = CAMPAIGN_TRACKING_PARAMS.get(param)
        if ga_name in request.GET:
            campaign_params[param] = request.GET[ga_name]

    # store campaign tracking parameters in session
    request.session[CAMPAIGN_PARAMS_KEY] = campaign_params

    # add campaign tracking parameters if provided
    params.update(campaign_params)

    # construct the gif hit url
    ga_url = "https://www.google-analytics.com/collect"
    utm_url = ga_url + "?&" + urlencode(params)
    ga_logging_enabled = False
    if hasattr(settings, 'ENABLE_GA_LOGGING') and settings.ENABLE_GA_LOGGING:
        log = structlog.get_logger()
        log.msg('GA_URL: %s' % utm_url, user_agent=user_agent)
        ga_logging_enabled = True

    locale = get_language_from_request(request)

    return {'utm_url': utm_url,
            'user_agent': user_agent,
            'language': locale or settings.LANGUAGE_CODE,
            'visitor_id': visitor_id,
            'COOKIE_USER_PERSISTENCE': COOKIE_USER_PERSISTENCE,
            'COOKIE_NAME': COOKIE_NAME,
            'COOKIE_PATH': COOKIE_PATH,
            'ga_logging_enabled': ga_logging_enabled
            }
