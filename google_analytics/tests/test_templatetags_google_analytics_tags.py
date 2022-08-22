from urllib.parse import parse_qs

from django.template import Context, Template
from django.test import RequestFactory, TestCase, override_settings
from google_analytics.templatetags.google_analytics_tags import \
    google_analytics


class GoogleAnalyticsTagsTestCase(TestCase):
    TEMPLATE = Template(
        "{% load google_analytics_tags %}{% google_analytics %}"
    )

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

    def test_tracking_code_used_if_passed_in(self):
        context = Context({'request': self.request})
        rendered_template = google_analytics(context, tracking_code='my-code')
        self.assertIn('tracking_code=my-code', rendered_template)

    def test_tracking_code_defaults_to_settings(self):
        context = Context({'request': self.request})
        rendered_template = google_analytics(context)
        self.assertIn('tracking_code=ua-test-id', rendered_template)

    @override_settings(GOOGLE_ANALYTICS={})
    def test_template_blank_if_tracking_code_unset(self):
        context = Context({'request': self.request})
        rendered_template = google_analytics(context)
        self.assertEqual('', rendered_template)

    def test_query_param(self):
        request = self.factory.get('/?test=abc')
        context = Context({'request': request})

        rendered_template = google_analytics(context, tracking_code='my-code')

        parsed_qs = parse_qs(rendered_template)
        self.assertEqual(parsed_qs['tracking_code'][0], "my-code")
        self.assertEqual(parsed_qs['p'][0], "/?test=abc")

    def test_query_param_with_multiple_values_with_same_key(self):
        request = self.factory.get('/?test=abc&test=xyz')
        context = Context({'request': request})

        rendered_template = google_analytics(context, tracking_code='my-code')

        parsed_qs = parse_qs(rendered_template)
        self.assertEqual(parsed_qs['tracking_code'][0], "my-code")
        self.assertEqual(parsed_qs['p'][0], "/?test=abc&test=xyz")

    def test_query_param_with_campaign(self):
        request = self.factory.get(
            '/en/?utm_content=content&utm_term=term&utm_source=source'
            '&utm_medium=medium&utm_campaign=campaign')
        context = Context({'request': request})

        rendered_template = google_analytics(context, tracking_code='my-code')

        parsed_qs = parse_qs(rendered_template)
        self.assertEqual(parsed_qs['tracking_code'][0], "my-code")
        self.assertEqual(parsed_qs['p'][0], "/en/")
        self.assertEqual(parsed_qs['utm_content'][0], "content")
        self.assertEqual(parsed_qs['utm_term'][0], "term")
        self.assertEqual(parsed_qs['utm_source'][0], "source")
        self.assertEqual(parsed_qs['utm_medium'][0], "medium")
        self.assertEqual(parsed_qs['utm_campaign'][0], "campaign")
