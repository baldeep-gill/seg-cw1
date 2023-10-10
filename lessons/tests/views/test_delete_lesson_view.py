from django.test import TestCase
from django.urls import reverse
from lessons.models import Admin, Student, Lesson, Invoice

class DeleteLessonViewTestCase(TestCase):
    """Unit tests for delete lesson view"""

    fixtures = [
        'lessons/tests/fixtures/admin_user.json',
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/default_invoice.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.student = Student.objects.get(email="johndoe@example.org")
        self.admin = Admin.objects.get(email="student_admin@example.org")
        self.form_input = {
            "date": "2023-12-03 12:00:00Z",
            "duration": 60,
            "topic": "Piano",
            "teacher": "Mr Bob"
        }

        self.lesson = Lesson(
            student = Student.objects.get(email="johndoe@example.org"),
            invoice = Invoice.objects.get(invoice_number=100),
            date = "2022-12-03 12:00:00Z",
            duration = 1,
            topic = "Drums",
            teacher = "Mr Jim"
        )

        self.lesson.save()
        self.url = reverse('delete_lessons', kwargs={'lesson_id': self.lesson.id})

    def test_lesson_url(self):
        self.assertEqual(self.url, f'/admin/lessons/delete/{self.lesson.id}')

    def test_delete_lesson(self):
        redirect_url = reverse('admin_lessons')
        self.client.force_login(self.admin)
        before = Lesson.objects.count()
        response = self.client.get(self.url)
        after = Lesson.objects.count()
        self.assertEqual(after, before-1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_delete_invalid_lesson(self):
        self.client.force_login(self.admin)
        url = reverse('delete_lessons', kwargs={'lesson_id': 9999})
        redirect_url = reverse('admin_lessons')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_reject_student_access(self):
        self.client.force_login(self.student)
        redirect_url = reverse("student_home")
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_not_logged_in_get_lesson(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)