from django.test import TestCase
from django.urls import reverse
from lessons.forms import LessonRequestForm
from lessons.models import Student, LessonRequest

class LessonRequestViewTestCase(TestCase):
    """Tests for the lesson request view"""

    fixtures = ['lessons/tests/fixtures/default_student.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.url = reverse('lesson_request')
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
        self.assertEqual(self.url, '/lesson_request/')

    def test_get_request_page(self):
        self.client.login(username=self.student.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "lesson_request.html")
        form = response.context['form']
        self.assertTrue(isinstance(form, LessonRequestForm))
        self.assertFalse(form.is_bound)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_unsuccessful_post(self):
        self.form_input['interval'] = -1
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_request.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LessonRequestForm))
        self.assertTrue(form.is_bound)
        
    