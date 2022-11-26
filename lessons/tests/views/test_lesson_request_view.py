from django.test import TestCase
from django.urls import reverse
from lessons.forms import LessonRequestForm
from lessons.models import Student, Admin, LessonRequest

class LessonRequestViewTestCase(TestCase):
    """Tests for the lesson request view"""

    fixtures = [
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/admin_user.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.url = reverse('lesson_request')
        self.student = Student.objects.get(email="johndoe@example.org")
        self.admin = Admin.objects.get(email="student_admin@example.org")
        self.form_input = {
            "availability": "Monday",
            "lessonNum": 3,
            "interval": 1,
            "duration": 60,
            "topic": "piano",
            "teacher": "Mr Bob"
        }

    def test_request_url(self):
        self.assertEqual(self.url, '/student/lesson_request/')

    def test_get_request(self):
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "lesson_request.html")
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(isinstance(form, LessonRequestForm))
        self.assertFalse(form.is_bound)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_not_logged_in_get_request(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccessful_post(self):
        self.form_input['interval'] = -1
        self.client.force_login(self.student)
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_request.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LessonRequestForm))
        self.assertTrue(form.is_bound)

    def test_admin_reject_access(self):
        self.client.force_login(self.admin)
        redirect_url = reverse("admin_home")
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_post(self):
        redirect_url = reverse("student_home")
        self.client.force_login(self.student)
        before = LessonRequest.objects.count()
        response = self.client.post(self.url, self.form_input)
        after = LessonRequest.objects.count()
        self.assertEqual(before+1, after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        