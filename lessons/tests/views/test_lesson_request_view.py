from django.test import TestCase
from django.urls import reverse
from lessons.forms import LessonRequestForm
from lessons.models import Student, LessonRequest

class LessonRequestViewTestCase(TestCase):
    """Tests for the lesson request view"""

    def setUp(self):
        super(TestCase, self).setUp()
        self.url = reverse('lesson_request')

    def test_login_url(self):
        self.assertEqual(self.url, '/student/lesson_request/')