from django.test import TestCase
from django.urls import reverse
from lessons.models import Student, Admin, Lesson, Invoice

class ShowScheduleTestCase(TestCase):
    """Tests for the show schedule view"""

    fixtures = [
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/default_invoice.json',
        'lessons/tests/fixtures/admin_user.json'
    ]

    def setUp(self):
        self.student = Student.objects.get(email='johndoe@example.org')
        self.admin = Admin.objects.get(email="student_admin@example.org")
        self.url = reverse('show_schedule')

        self.lesson = Lesson(
            student = Student.objects.get(email="johndoe@example.org"),
            invoice = Invoice.objects.get(invoice_number=100),
            date = "2022-12-03 12:00:00Z",
            duration = 1,
            topic = "Drums",
            teacher = "Mr Jim"
        )
        self.lesson.save()
    
    def test_schedule_url(self):
        self.assertEqual(self.url,'/student/schedule/')

    def test_get_schedule(self):
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_schedule.html')

    def test_not_logged_in_get_schedule(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_reject_admin_access(self):
        self.client.force_login(self.admin)
        redirect_url = reverse("admin_home")
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)