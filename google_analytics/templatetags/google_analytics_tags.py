import urllib
import urlparse

from django import template
from django.core.urlresolvers import reverse
from django.conf import settings

from google_analytics import (GA_CAMPAIGN_TRACKING_PARAMS,
                              UA_CAMPAIGN_TRACKING_PARAMS)


register = template.Library()


class GoogleAnalyticsNode(template.Node):
    """Tag node for building the link to the internal google analytics
    image.

    """

    def __init__(self, debug, use_ua):
        self.debug = debug
        self.use_ua = use_ua

    def render(self, context):
        # Trivial case
        try:
            assert settings.GOOGLE_ANALYTICS['google_analytics_id']
        except:
            return ''

        # attempt get the request from the context
        request = context.get('request', None)
        if request is None:
            raise RuntimeError("Request context required")
        # intialise the parameters collection
        params = {}
        if self.use_ua:
            campaign_tracking_params = UA_CAMPAIGN_TRACKING_PARAMS
        else:
            campaign_tracking_params = GA_CAMPAIGN_TRACKING_PARAMS
        # collect the campaign tracking parameters from the request
        for param in campaign_tracking_params:
            value = request.REQUEST.get(param, None)
            if value:
                params[param] = value
        # pass on the referer if present
        referer = request.META.get('HTTP_REFERER', None)
        if referer:
            params['r'] = referer
        # remove collected parameters from the path and pass it on
        path = request.path
        parsed_url = urlparse.urlparse(path)
        query = urlparse.parse_qs(parsed_url.query)
        for param in params:
            if param in query:
                del query[param]
        query = urllib.urlencode(query)
        new_url = parsed_url._replace(query=query)
        params['p'] = new_url.geturl()
        # append the UA parameter if requested
        if self.use_ua:
            params['ua'] = 1
        # append the debug parameter if requested
        if self.debug:
            params['gadebug'] = 1
        # build and return the url
        url = reverse('google-analytics')
        if len(params) > 0:
            url += '?' + urllib.urlencode(params)
        return url


@register.tag
def google_analytics(parser, token):
    """Parser method that build a GoogleAnalyticsNode for rendering."""
    bits = token.split_contents()
    # collect parameters if available
    debug = 'False'
    if len(bits) > 1:
        debug = bits[1]
    if len(bits) > 2:
        use_ua = bits[2]
    if len(debug) > 0:
        debug = (debug[0].lower() == 't')
    if len(use_ua) > 0:
        use_ua = (use_ua[0].lower() == 't')
    # build and return the node
    return GoogleAnalyticsNode(debug)
