from bs4 import BeautifulSoup

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from google_analytics.tasks import send_ga_tracking
from google_analytics.utils import build_ga_params, set_cookie


class GoogleAnalyticsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if hasattr(settings, 'GOOGLE_ANALYTICS_IGNORE_PATH'):
            exclude = [p for p in settings.GOOGLE_ANALYTICS_IGNORE_PATH
                       if request.path.startswith(p)]
            if any(exclude):
                return response

        # get the account id
        try:
            account = settings.GOOGLE_ANALYTICS['google_analytics_id']
        except (KeyError, TypeError):
            raise Exception("No Google Analytics ID configured")

        try:
            title = BeautifulSoup(
                response.content, "html.parser").html.head.title.text
        except AttributeError:
            title = None

        path = request.path
        referer = request.META.get('HTTP_REFERER', '')
        params = build_ga_params(
            request, account, path=path, referer=referer, title=title)
        response = set_cookie(params, response)
        send_ga_tracking.delay(params)
        return response
