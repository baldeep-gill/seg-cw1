from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from lessons.models import Student, Admin, Lesson, Invoice

class BalanceView(TestCase):
    """Tests of the balance view."""

    fixtures = [
        'lessons/tests/fixtures/default_student.json', 
        'lessons/tests/fixtures/other_students.json',
        'lessons/tests/fixtures/admin_user.json'
        ]

    def setUp(self):
        self.url = reverse('balance')
        self.student = Student.objects.get(email="johndoe@example.org")
        self.other_student = Student.objects.get(email="janedoe@example.org")
        self.admin = Admin.objects.get(email="student_admin@example.org")

    def test_request_url(self):
        self.assertEqual(self.url, '/student/balance/')

    def test_access_without_login(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_get_request_as_an_admin(self):
        self.client.login(username=self.admin.email, password='Password123')
        redirect_url = reverse("admin_home")
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_access_with_login(self):
        self.client.login(username=self.student.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'balance.html')

    def test_balance_with_no_lessons(self):
        self.client.login(username=self.student.email, password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'you owe nothing, for now...')

    def test_balance_with_lessons(self):
        new_invoice = Invoice.objects.create(
            student=self.student,
            date=timezone.now(),
            invoice_number=1,
            unique_reference_number=f'{self.student.id}-{1}'
        )
        Lesson.objects.create(
                    student=self.student,
                    invoice=new_invoice,
                    date=timezone.now(),
                    duration=60,
                    topic='topic',
                    teacher='teacher'
                )
        self.client.login(username=self.student.email, password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, '£')
    
    def test_each_student_see_their_own_requests(self):
        new_invoice = Invoice.objects.create(
            student=self.student,
            date=timezone.now(),
            invoice_number=1,
            unique_reference_number=f'{self.student.id}-{1}'
        )
        Lesson.objects.create(
                    student=self.student,
                    invoice=new_invoice,
                    date=timezone.now(),
                    duration=60,
                    topic='topic',
                    teacher='teacher'
                )
        self.client.login(username=self.other_student.email, password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'you owe nothing, for now...')


