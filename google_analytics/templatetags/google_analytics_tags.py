from six.moves.urllib.parse import parse_qs, urlencode, urlparse

from django import template
from django.conf import settings
from django.urls import reverse
from google_analytics import CAMPAIGN_TRACKING_PARAMS

register = template.Library()


@register.simple_tag(takes_context=True)
def google_analytics(context, tracking_code=None, debug=False):
    if not tracking_code:
        try:
            assert settings.GOOGLE_ANALYTICS['google_analytics_id']
        except KeyError:
            return ''
    # attempt get the request from the context
    request = context.get('request', None)
    if request is None:
        raise RuntimeError("Request context required")
    # intialise the parameters collection
    params = {}
    # collect the campaign tracking parameters from the request
    for param in CAMPAIGN_TRACKING_PARAMS:
        value = request.GET.get(param, None)
        if value:
            params[param] = value
    # pass on the referer if present
    referer = request.META.get('HTTP_REFERER', None)
    if referer:
        params['r'] = referer
    # remove collected parameters from the path and pass it on
    path = request.path
    parsed_url = urlparse(path)
    query = parse_qs(parsed_url.query)
    for param in params:
        if param in query:
            del query[param]
    query = urlencode(query)
    new_url = parsed_url._replace(query=query)
    params['p'] = new_url.geturl()
    params['tracking_code'] = tracking_code or settings.GOOGLE_ANALYTICS[
        'google_analytics_id']
    # append the debug parameter if requested
    if debug:
        params['utmdebug'] = 1
    # build and return the url
    url = reverse('google-analytics')
    if params:
        url += '?&' + urlencode(params)
    return url
