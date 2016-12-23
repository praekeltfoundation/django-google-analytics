import random
import time
import urllib
import uuid

from django.conf import settings
from django.utils.translation import get_language_from_request

from google_analytics import CAMPAIGN_TRACKING_PARAMS

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


def build_ga_params(request, account, path=None, event=None, referer=None, title=None):
    meta = request.META
    # determine the domian
    domain = meta.get('HTTP_HOST', '')

    # determine the referrer
    referer = referer or request.GET.get('r', '')

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
    if 'HTTP_X_FORWARDED_FOR' in meta:
        client_ip = meta.get('HTTP_X_FORWARDED_FOR', '')
    else:
        client_ip = meta.get('REMOTE_ADDR', '')

    # build the parameter collection
    params = {
        'v': VERSION,
        'z': str(random.randint(0, 0x7fffffff)),
        'dh': domain,
        'sr': '',
        'dr': referer,
        'dp': path,
        'tid': account,
        'cid': visitor_id,
        'uip': custom_uip or client_ip,
    }

    # add page title if supplied
    if title:
        params.update({'dt': title})

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
        if param in request.GET:
            campaign_params[param] = request.GET[param]

    # store campaign tracking parameters in session
    request.session[CAMPAIGN_PARAMS_KEY] = campaign_params

    # add campaign tracking parameters if provided
    params.update(campaign_params)

    # construct the gif hit url
    ga_url = "http://www.google-analytics.com/collect"
    utm_url = ga_url + "?&" + urllib.urlencode(params)
    locale = get_language_from_request(request)
    
    return {'utm_url': utm_url,
            'user_agent': user_agent,
            'language': locale or settings.LANGUAGE_CODE,
            'visitor_id': visitor_id,
            'COOKIE_USER_PERSISTENCE': COOKIE_USER_PERSISTENCE,
            'COOKIE_NAME': COOKIE_NAME,
            'COOKIE_PATH': COOKIE_PATH,
            }
