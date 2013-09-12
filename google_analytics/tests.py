from httplib2 import Http
from urllib import urlencode

from django.test import TestCase, Client
from django.conf import settings
from django.test.client import RequestFactory

from mock import patch, Mock

from google_analytics.templatetags.google_analytics_tags \
    import GoogleAnalyticsNode


class BaseTestCase(TestCase):
    HEADERS = {
        'HTTP_USER_AGENT': 'TestClient',
        'HTTP_X_FORWARDED_FOR': '192.168.32.64',
        'HTTP_ACCEPT_LANGUAGE': 'en-GB',
        'HTTP_HOST': 'www.example.com',
        'HTTP_REFERER': 'www.referer.com'
    }
    PATH = '/index/'

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self._request = Http.request
        Http.request = Mock()
        Http.request.return_value = ('', '')
        self.factory = RequestFactory(**self.HEADERS)
        no_ref_headers = self.HEADERS.copy()
        del no_ref_headers['HTTP_REFERER']
        self.client = Client(**no_ref_headers)

    def tearDown(self):
        super(BaseTestCase, self).tearDown()
        Http.request = self._request

    def create_gif_url(self):
        request = self.factory.get(self.PATH)
        node = GoogleAnalyticsNode(debug=False)
        url = node.render(context={'request': request})
        # check that path and referer are added to the gif url
        self.assertIn(urlencode({'p': self.PATH}), url)
        self.assertIn(urlencode({'r': self.HEADERS['HTTP_REFERER']}), url)
        return url

    def check_ga_request_headers(self):
        headers = Http.request.call_args[1]['headers']
        self.assertEqual(headers['User-Agent'],
                         self.HEADERS['HTTP_USER_AGENT'])
        self.assertEqual(headers['X-Forwarded-For'],
                         self.HEADERS['HTTP_X_FORWARDED_FOR'])
        self.assertEqual(headers['Accept-Language'],
                         self.HEADERS['HTTP_ACCEPT_LANGUAGE'])

    def test_visitor_cookie_persistence(self):
        pass


class GATestCase(BaseTestCase):

    def test_build_url(self):
        ga_url = self.create_gif_url()
        response = self.client.get(ga_url)
        self.assertEqual(response['Content-Type'], 'image/gif')
        self.assertEqual(response.status_code, 200)
        self.check_ga_request_headers()
        # this call should be a GET request
        self.assertEqual(Http.request.call_args[0][1].upper(), 'GET')
        # check that all the parameters are in the url
        params_exist = ['utmsr', 'utme', 'utmvid', 'utmn', 'utmwv']
        params_equal = {
            'utmhn': self.HEADERS['HTTP_HOST'],
            'utmr': self.HEADERS['HTTP_REFERER'],
            'utmp': self.PATH,
            'utmac': settings.GOOGLE_ANALYTICS['google_analytics_id'],
            'utmip': self.HEADERS['HTTP_X_FORWARDED_FOR'],
        }
        url = Http.request.call_args[0][0]
        for param in params_exist:
            self.assertIn(param, url)
        for param, val in params_equal.iteritems():
            self.assertIn(urlencode({param: val}), url)


def custom_dimensions(request):
    return {}


class UATestCase(BaseTestCase):

    def setUp(self):
        super(UATestCase, self).setUp()
        self.settings_context = self.settings(GOOGLE_ANALYTICS={
            'google_analytics_id': 'UA-00000000-00',
            'USE_UA': True,
            'CUSTOM_DATA_PROVIDERS': ('tests.custom_dimensions', ),
        })
        self.settings_context.__enter__()

    def tearDown(self):
        super(UATestCase, self).tearDown()
        self.settings_context.__exit__(None, None, None)

    def test_build_url(self):
        ua_url = self.create_gif_url()
        response = self.client.get(ua_url)
        self.assertEqual(response['Content-Type'], 'image/gif')
        self.assertEqual(response.status_code, 200)
        self.check_ga_request_headers()
        # this call should be a POST request
        self.assertEqual(Http.request.call_args[0][1].upper(), 'POST')
        # check that all the parameters are in the url
        params_exist = ['utmsr', 'utme', 'utmvid', 'utmn', 'utmwv']
        params_equal = {
            'utmhn': self.HEADERS['HTTP_HOST'],
            'utmr': self.HEADERS['HTTP_REFERER'],
            'utmp': self.PATH,
            'utmac': settings.GOOGLE_ANALYTICS['google_analytics_id'],
            'utmip': self.HEADERS['HTTP_X_FORWARDED_FOR'],
        }
        url = Http.request.call_args[0][0]
        for param in params_exist:
            self.assertIn(param, url)
        for param, val in params_equal.iteritems():
            self.assertIn(urlencode({param: val}), url)

    def test_custom_data(self):
        pass
