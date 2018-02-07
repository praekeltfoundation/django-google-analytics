# -*- coding: utf-8 -*-

import responses

from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.test.client import Client
from django.test.client import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

from google_analytics.utils import COOKIE_NAME, build_ga_params
from six.moves.urllib.parse import parse_qs
from google_analytics.templatetags.google_analytics_tags import google_analytics # noqa
from google_analytics.middleware import GoogleAnalyticsMiddleware


class GoogleAnalyticsTestCase(TestCase):

    def make_fake_request(self, url, headers={}):
        """
        We don't have any normal views, so we're creating fake
        views using django's RequestFactory
        """
        rf = RequestFactory()
        request = rf.get(url, **headers)
        session_middleware = SessionMiddleware()
        session_middleware.process_request(request)
        request.session.save()
        return request

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

    @override_settings(
        MIDDLEWARE_CLASSES=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'google_analytics.middleware.GoogleAnalyticsMiddleware'
        ],
        TASK_ALWAYS_EAGER=True,
        BROKER_URL='memory://')
    @responses.activate
    def test_ga_middleware(self):
        responses.add(
            responses.GET, 'http://www.google-analytics.com/collect',
            body='',
            status=200)

        headers = {'HTTP_X_IORG_FBS_UIP': '100.100.200.10'}
        request = self.make_fake_request(
            '/sections/deep-soul/ما-مدى-جاهزيتك-للإنترنت/', headers)

        middleware = GoogleAnalyticsMiddleware()
        html = ("<html><head><title>"
                "ما-مدى-جاهزيتك-للإنترنت</title></head></html>")
        response = middleware.process_response(request, HttpResponse(html))
        uid = response.cookies.get(COOKIE_NAME).value

        self.assertEqual(len(responses.calls), 1)

        ga_url = responses.calls[0].request.url

        self.assertEqual(parse_qs(ga_url).get('t'), ['pageview'])
        self.assertEqual(
            parse_qs(ga_url).get('dp'), [
                '/sections/deep-soul/%D9%85%D8%A7-%D9%85%D8%AF%D9%89-'
                '%D8%AC%D8%A7%D9%87%D8%B2%D9%8A%D8%AA%D9%83-%D9%84%D9'
                '%84%D8%A5%D9%86%D8%AA%D8%B1%D9%86%D8%AA/'])
        self.assertEqual(parse_qs(ga_url).get('dt'), [
            '%D9%85%D8%A7-%D9%85%D8%AF%D9%89-%D8%AC%D8%A7%D9%87%D8%B2%D9%8A%D8'
            '%AA%D9%83-%D9%84%D9%84%D8%A5%D9%86%D8%AA%D8%B1%D9%86%D8%AA'])
        self.assertEqual(parse_qs(ga_url).get('tid'), ['ua-test-id'])
        self.assertEqual(parse_qs(ga_url).get('cid'), [uid])
        self.assertEqual(parse_qs(ga_url).get('uip'), ['100.100.200.10'])

    @override_settings(
        MIDDLEWARE_CLASSES=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'google_analytics.middleware.GoogleAnalyticsMiddleware'
        ],
        TASK_ALWAYS_EAGER=True,
        BROKER_URL='memory://')
    @responses.activate
    def test_build_ga_params_for_title_encoding(self):
        responses.add(
            responses.GET, 'http://www.google-analytics.com/collect',
            body='',
            status=200)

        headers = {
            'HTTP_X_IORG_FBS_UIP': '100.100.200.10',
            'HTTP_X_DCMGUID': '0000-0000-0000-0000'}
        request = self.make_fake_request(
            '/sections/deep-soul/ما-مدى-جاهزيتك-للإنترنت/', headers)

        middleware = GoogleAnalyticsMiddleware()
        html = "<html><head><title>title</title></head></html>"
        response = middleware.process_response(request, HttpResponse(html))

        ga_dict = build_ga_params(
            request, response, 'ua-test-id', '/some/path/',
            referer='/some/path/', title='ما-مدى-جاهزيتك-للإنترنت')
        self.assertEqual(parse_qs(ga_dict.get('utm_url')).get('dt'), [
            '%D9%85%D8%A7-%D9%85%D8%AF%D9%89-%D8%AC%D8%A7%D9%87%D8%B2%D9%8A%D8'
            '%AA%D9%83-%D9%84%D9%84%D8%A5%D9%86%D8%AA%D8%B1%D9%86%D8%AA'])

    @responses.activate
    def test_build_ga_params_for_user_id(self):
        request = self.make_fake_request('/somewhere/')

        ga_dict_without_uid = build_ga_params(
            request, 'ua-test-id', '/some/path/',)

        ga_dict_with_uid = build_ga_params(
            request, 'ua-test-id', '/some/path/', user_id='402-3a6')

        self.assertEqual(
            parse_qs(ga_dict_without_uid.get('utm_url')).get('uid'), None)
        self.assertEqual(
            parse_qs(ga_dict_with_uid.get('utm_url')).get('uid'), ['402-3a6'])

    @override_settings(MIDDLEWARE_CLASSES=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'google_analytics.middleware.GoogleAnalyticsMiddleware'
    ])
    @responses.activate
    def test_ga_middleware_no_title(self):
        responses.add(
            responses.GET, 'http://www.google-analytics.com/collect',
            body='',
            status=200)

        headers = {'HTTP_X_IORG_FBS_UIP': '100.100.200.10'}
        request = self.make_fake_request('/somewhere/', headers)

        middleware = GoogleAnalyticsMiddleware()
        response = middleware.process_response(request, HttpResponse())
        uid = response.cookies.get(COOKIE_NAME).value

        self.assertEqual(len(responses.calls), 1)

        ga_url = responses.calls[0].request.url

        self.assertEqual(parse_qs(ga_url).get('t'), ['pageview'])
        self.assertEqual(parse_qs(ga_url).get('dp'), ['/somewhere/'])
        self.assertEqual(parse_qs(ga_url).get('dt'), None)
        self.assertEqual(parse_qs(ga_url).get('tid'), ['ua-test-id'])
        self.assertEqual(parse_qs(ga_url).get('cid'), [uid])
        self.assertEqual(parse_qs(ga_url).get('uip'), ['100.100.200.10'])

    @override_settings(MIDDLEWARE_CLASSES=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'google_analytics.middleware.GoogleAnalyticsMiddleware'
    ], GOOGLE_ANALYTICS_IGNORE_PATH=['/ignore-this/'])
    def test_ga_middleware_ignore_path(self):
        request = self.make_fake_request('/ignore-this/somewhere/')
        middleware = GoogleAnalyticsMiddleware()
        middleware.process_response(request, HttpResponse())

        self.assertEqual(len(responses.calls), 0)

    @override_settings(MIDDLEWARE_CLASSES=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'google_analytics.middleware.GoogleAnalyticsMiddleware'
    ], GOOGLE_ANALYTICS=None)
    def test_ga_middleware_no_account_set(self):
        client = Client()
        with self.assertRaises(Exception):
            client.get('/google-analytics/?p=%2Fhome&r=test.com')
