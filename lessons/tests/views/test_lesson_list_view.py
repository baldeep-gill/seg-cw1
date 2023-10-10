from django.test import TestCase
from django.urls import reverse
from lessons.models import Student
from lessons.tests.helpers import reverse_with_next

class LessonList(TestCase):
    """Tests of the lesson list view."""

    fixtures = ['lessons/tests/fixtures/default_student.json']

    def setUp(self):
        self.url = reverse('lesson_list')
        self.user = Student.objects.get(email="johndoe@example.org")
    
    def test_lessons_url(self):
        self.assertEqual(self.url, '/student/lessons/list')

    def test_get_lessons_without_login(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_lessons_with_log_in(self):
        self.client.login(username=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'successful_lessons_list.html')
