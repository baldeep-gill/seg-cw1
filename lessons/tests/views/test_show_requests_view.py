from django.test import TestCase
from django.urls import reverse
from lessons.models import Student
from lessons.tests.helpers import create_requests

class LessonRequestViewTestCase(TestCase):
    """Tests for the lesson request view"""

    fixtures = ['lessons/tests/fixtures/default_student.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.url = reverse('show_requests')
        self.student = Student.objects.get(email="johndoe@example.org")
        self.form_input = {
            "availability": "Monday",
            "lessonNum": 3,
            "interval": 1,
            "duration": 60,
            "topic": "piano",
            "teacher": "Mr Bob"
        }

    def test_request_url(self):
        self.assertEqual(self.url, '/student/requests/')

    def test_get_request(self):
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "show_requests.html")

    def test_not_logged_in_get_request(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_page_shows_requests(self):
        self.client.force_login(self.student)
        create_requests(self.student, 100, 105)
        response = self.client.get(self.url)
        for count in range(100, 105):
            self.assertContains(response, f'Request__{count}')
