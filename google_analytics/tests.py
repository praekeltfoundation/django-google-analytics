from httplib2 import Http

from django.test import TestCase, Client
from django.test.client import RequestFactory

from mock import patch, Mock

from google_analytics.templatetags.google_analytics_tags \
    import GoogleAnalyticsNode


class BaseTestCase(TestCase):
    CLIENT_HEADERS = {
        'HTTP_USER_AGENT': 'TestClient',
        'HTTP_X_FORWARDED_FOR': '192.168.32.64',
        'HTTP_ACCEPT_LANGUAGE': 'en-GB',
        'HTTP_HOST': 'www.example.com',
    }
    FACTORY_HEADERS = CLIENT_HEADERS.copy()
    FACTORY_HEADERS.update({
        'HTTP_REFERER': 'www.referer.com'
    })
    PATH = '/index/'

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self._request = Http.request
        Http.request = Mock()
        Http.request.return_value = ('', '')
        self.client = Client(**self.CLIENT_HEADERS)
        self.factory = RequestFactory(**self.FACTORY_HEADERS)

    def tearDown(self):
        super(BaseTestCase, self).tearDown()
        Http.request = self._request

    def create_gif_url(self):
        request = self.factory.get(self.PATH)
        node = GoogleAnalyticsNode(debug=False)
        url = node.render(context={'request': request})
        # check that path and referer are added to the gif url
        self.assertIn('p=%s' % self.PATH, url)
        self.assertIn('r=%s' % self.FACTORY_HEADERS['HTTP_REFERER'])
        return url


class GATestCase(BaseTestCase):

    def test_build_url(self):
        ga_url = self.create_gif_url()
        print ga_url


def custom_dimensions(request):
    return {}


class UATestCase(BaseTestCase):

    def setUp(self):
        super(GATestCase, self).setUp()
        self.settings_context = self.settings(GOOGLE_ANALYTICS={
            'google_analytics_id': 'UA-00000000-00',
            'USE_UA': True,
            'CUSTOM_DATA_PROVIDERS': ('tests.custom_dimensions', ),
        })
        self.settings_context.__enter__()

    def tearDown(self):
        super(GATestCase, self).tearDown()
        self.settings_context.__exit__()

    def test_custom_data(self):
        pass
