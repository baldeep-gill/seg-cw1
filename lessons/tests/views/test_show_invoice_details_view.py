from django.test import TestCase
from django.urls import reverse
from lessons.models import Student
from lessons.tests.helpers import create_invoices

class ShowInvoiceLessonsTestCase(TestCase):
    """Tests for the show invoices view"""

    fixtures = ['lessons/tests/fixtures/default_student.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.url = reverse('show_invoices')
        self.student = Student.objects.get(email="johndoe@example.org")

    def test_request_url(self):
        self.assertEqual(self.url, '/student/invoices/')

    def test_get_request(self):
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "invoices_list.html")

    def test_not_logged_in_get_request(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_page_shows_invoices(self):
        start_invoice_number, end_invoice_number = 100,105
        self.client.force_login(self.student)
        create_invoices(self.student, start_invoice_number, end_invoice_number)
        response = self.client.get(self.url)
        for invoice_number in range(start_invoice_number, end_invoice_number):
            self.assertContains(response, invoice_number)