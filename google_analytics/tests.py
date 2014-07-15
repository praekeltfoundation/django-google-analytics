from django.test import TestCase
from django.test.client import Client
from google_analytics.utils import COOKIE_NAME
from urlparse import parse_qs


class GoogleAnalyticsTestCase(TestCase):
    def SetUp(self):
        pass

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
        client = Client()
        response = client.get(
            '/google-analytics/?p=%2Fhome&utmdebug=True&r=test.com')
        ga_url1 = response.get('X-GA-MOBILE-URL')

        response = client.get(
            '/google-analytics/?p=%2Fblog&utmdebug=True&r=test.com')
        ga_url2 = response.get('X-GA-MOBILE-URL')

        self.assertEqual(
            parse_qs(ga_url1).get('cid'),
            parse_qs(ga_url2).get('cid'))
        self.assertEqual(parse_qs(ga_url1).get('t'), ['pageview'])
        self.assertEqual(parse_qs(ga_url1).get('dr'), ['test.com'])
        self.assertEqual(parse_qs(ga_url1).get('dp'), ['/home'])
        self.assertEqual(parse_qs(ga_url2).get('dp'), ['/blog'])
        self.assertEqual(parse_qs(ga_url1).get('tid'), ['ua-test-id'])
