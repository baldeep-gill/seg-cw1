from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from lessons.models import Student, Admin, Lesson, Invoice, Transfer
from lessons.helpers import find_next_available_transfer_id

class AdminStudentPaymentsView(TestCase):
    """Tests of the balance view."""

    fixtures = [
        'lessons/tests/fixtures/default_student.json', 
        'lessons/tests/fixtures/other_students.json',
        'lessons/tests/fixtures/admin_user.json',
        ]

    def setUp(self):
        self.student = Student.objects.get(email="johndoe@example.org")
        self.url = reverse('student_payments', kwargs={"student_id": self.student.id})
        self.other_student = Student.objects.get(email="janedoe@example.org")
        self.admin = Admin.objects.get(email="student_admin@example.org")
        self.invoice = Invoice(
            date=timezone.now(),
            invoice_number=100,
            student_id=1
        )
        self.lesson = Lesson(
            student=self.student,
            invoice=self.invoice,
            duration=100,
            date=timezone.now()
        )
        next_transfer_id = find_next_available_transfer_id()
        self.transfer = Transfer(date_received=timezone.now(), transfer_id=next_transfer_id, verifier=self.admin, invoice=self.invoice, amount_received=self.invoice.price)

    def test_request_url(self):
        self.assertEqual(self.url, '/admin/payments/'+str(self.student.id))

    def test_access_without_login(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_get_request_as_an_student(self):
        self.client.login(username=self.student.email, password='Password123')
        redirect_url = reverse("student_home")
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_access_with_login(self):
        self.client.login(username=self.admin.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_student_payments.html')

    def test_student_view_with_no_invoice_or_transfer(self):
        self.client.login(username=self.admin.email, password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'No invoices or transfers')

    def test_student_view_with_invoice(self):
        self.invoice.save()
        self.lesson.save()
        
        self.client.login(username=self.admin.email, password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Invoice ' + self.invoice.unique_reference_number)
    
    def test_student_view_after_transfer_confirmed(self):
        self.invoice.save()
        self.lesson.save()
        self.transfer.save()
        self.client.login(username=self.admin.email, password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Transfer for invoice ' + self.invoice.unique_reference_number)


