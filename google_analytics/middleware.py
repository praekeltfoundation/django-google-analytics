from django.conf import settings
from google_analytics.utils import build_ga_params, set_cookie
from google_analytics.tasks import send_ga_tracking


class GoogleAnalyticsMiddleware(object):
    def process_response(self, request, response):
        if hasattr(settings, 'GOOGLE_ANALYTICS_IGNORE_PATH'):
            exclude = [p for p in settings.GOOGLE_ANALYTICS_IGNORE_PATH\
                        if request.path.startswith(p)]
            if any(exclude):
                return response

        path = request.path
        referer = request.META.get('HTTP_REFERER', '')
        params = build_ga_params(request, path=path, referer=referer)
        response = set_cookie(params, response)
        send_ga_tracking.delay(params)
        return response
