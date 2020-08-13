from django.template import Context, Template
from django.test import RequestFactory, TestCase, override_settings
from google_analytics.templatetags.google_analytics_tags import \
    google_analytics


class GoogleAnalyticsTagsTestCase(TestCase):
    TEMPLATE = Template(
        "{% load google_analytics_tags %}{% google_analytics %}"
    )

    def setUp(self):
        factory = RequestFactory()
        self.request = factory.get('/')

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
