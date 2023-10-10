from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from lessons.models import Student, Admin, Lesson, Invoice, Transfer
from lessons.helpers import find_next_available_transfer_id

class AdminAllBalancesView(TestCase):
    """Tests of the balance view."""

    fixtures = [
        'lessons/tests/fixtures/default_student.json', 
        'lessons/tests/fixtures/other_students.json',
        'lessons/tests/fixtures/admin_user.json',
        ]

    def setUp(self):
        self.student = Student.objects.get(email="johndoe@example.org")
        self.invoice = Invoice.objects.create(
            date=timezone.now(),
            invoice_number=100,
            student_id=1
        )
        self.lesson = Lesson.objects.create(
            student=self.student,
            invoice=self.invoice,
            duration=100,
            date=timezone.now()
        )
        self.url = reverse('approve_transaction', kwargs={"student_id": self.student.id, "invoice_id": self.invoice.invoice_number})
        self.admin = Admin.objects.get(email="student_admin@example.org")
        
        # At setup, the next transfer ID would be the ID of the Transfer that is created in a test
        self.next_transfer_id = find_next_available_transfer_id()

    def test_request_url(self):
        POST_URL = '/admin/payments' + "/" + str(self.student.id) + "/" + str(self.invoice.invoice_number)
        self.assertEqual(self.url, POST_URL)

    def test_access_without_login(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.post(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_get_request_as_an_student(self):
        self.client.login(username=self.student.email, password='Password123')
        redirect_url = reverse("student_home")
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # def test_access_with_login(self):
    #     self.client.login(username=self.admin.email, password='Password123')
    #     redirect_url = reverse('student_payments', kwargs={"student_id": self.student.id})
    #     response = self.client.get(self.url, follow=True)
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)