from django.test import TestCase
from django.urls import reverse
from lessons.forms import LessonRequestForm
from lessons.models import Student, LessonRequest

class LessonRequestViewTestCase(TestCase):
    """Tests for the lesson request view"""

    def setUp(self):
        super(TestCase, self).setUp()
        self.url = reverse('lesson_request')

    def test_request_url(self):
        self.assertEqual(self.url, '/lesson_request/')

    def test_get_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "lesson_request.html")
        form = response.context['form']
        self.assertTrue(isinstance(form, LessonRequestForm))
        self.assertFalse(form.is_bound)