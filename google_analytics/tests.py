import responses

from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.test.client import Client
from django.test.client import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

from google_analytics.utils import COOKIE_NAME
from urlparse import parse_qs
from google_analytics.templatetags.google_analytics_tags import google_analytics # noqa
from google_analytics.middleware import GoogleAnalyticsMiddleware


class GoogleAnalyticsTestCase(TestCase):

    def test_cookies_set_properly(self):
        client = Client()
        response = client.get(
            '/google-analytics/?p=%2Fhome&r=test.com')
        cookie_1 = str(response.client.cookies.get(COOKIE_NAME))

        response = client.get(
            '/google-analytics/?p=%2Fblog&utmdebug=True&r=test.com')
        cookie_2 = str(response.client.cookies.get(COOKIE_NAME))

        self.assertEqual(cookie_1[:62], cookie_2[:62])

    def test_ga_url(self):
        client = Client(HTTP_X_IORG_FBS_UIP='100.100.200.10')
        response = client.get(
            '/google-analytics/?p=%2Fhome&utmdebug='
            'True&r=test.com&tracking_code=ua-test-id')
        ga_url1 = response.get('X-GA-MOBILE-URL')
        response = client.get(
            '/google-analytics/?p=%2Fblog&utmdebug='
            'True&r=test.com&tracking_code=ua-test-id')
        ga_url2 = response.get('X-GA-MOBILE-URL')
        self.assertEqual(
            parse_qs(ga_url1).get('cid'),
            parse_qs(ga_url2).get('cid'))
        self.assertEqual(parse_qs(ga_url1).get('t'), ['pageview'])
        self.assertEqual(parse_qs(ga_url1).get('dr'), ['test.com'])
        self.assertEqual(parse_qs(ga_url1).get('dp'), ['/home'])
        self.assertEqual(parse_qs(ga_url2).get('dp'), ['/blog'])
        self.assertEqual(parse_qs(ga_url1).get('tid'), ['ua-test-id'])
        self.assertEqual(parse_qs(ga_url1).get('uip'), ['100.100.200.10'])

    def test_ga_template_tag(self):
        rf = RequestFactory()
        post_request = rf.post('/submit/', {'foo': 'bar'})
        url = google_analytics(
            {'request': post_request},
            tracking_code='ua-test-id', debug=True)
        self.assertEqual(parse_qs(url).get('tracking_code'), ['ua-test-id'])
        self.assertEqual(parse_qs(url).get('utmdebug'), ['1'])
        url = google_analytics(
            {'request': post_request},
            tracking_code='ua-test-id', debug=False)
        self.assertEqual(parse_qs(url).get('utmdebug'), None)

    @override_settings(MIDDLEWARE_CLASSES=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'google_analytics.middleware.GoogleAnalyticsMiddleware'
    ])
    @responses.activate
    def test_ga_middleware(self):
        def fake_request(url):
            """
            We don't have any normal views, so we're creating fake
            views using django's RequestFactory
            """
            rf = RequestFactory()
            request = rf.get(url)
            session_middleware = SessionMiddleware()
            session_middleware.process_request(request)
            request.session.save()
            return request

        responses.add(
            responses.GET, 'http://www.google-analytics.com/collect',
            body='',
            status=200)

        request = fake_request('/somewhere/')

        middleware = GoogleAnalyticsMiddleware()
        response = middleware.process_response(request, HttpResponse())
        uid = response.cookies.get(COOKIE_NAME).value

        self.assertEqual(len(responses.calls), 1)
        self.assertTrue(responses.calls[0].request.url.startswith((
            'http://www.google-analytics.com/collect?&'
            'uip=127.0.0.1&cid={0}&'
            't=pageview&dh=&v=1&tid=ua-test-id').format(uid)))

    @override_settings(MIDDLEWARE_CLASSES=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'google_analytics.middleware.GoogleAnalyticsMiddleware'
    ], GOOGLE_ANALYTICS=None)
    def test_ga_middleware_no_account_set(self):
        client = Client()
        with self.assertRaises(Exception):
            client.get('/google-analytics/?p=%2Fhome&r=test.com')
