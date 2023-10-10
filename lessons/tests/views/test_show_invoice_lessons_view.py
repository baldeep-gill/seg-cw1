from django.test import TestCase
from django.urls import reverse
from lessons.models import Student, Invoice, Lesson
from lessons.tests.helpers import create_invoices, create_lesson_set

class ShowInvoiceLessonsTestCase(TestCase):
    """Tests for the show invoices view"""

    fixtures = ['lessons/tests/fixtures/default_student.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.student = Student.objects.get(email="johndoe@example.org")
        self.start_lesson_number, self.end_lesson_number = 100,105
        create_lesson_set(self.student,self.start_lesson_number,self.end_lesson_number)
        self.invoice = Invoice.objects.filter(student=self.student).first()
        self.url = reverse('show_invoice_lessons', kwargs={'invoice_id': self.invoice.id})


    def test_request_url(self):
        self.assertEqual(self.url, f'/student/invoices/{self.invoice.id}')

    def test_get_request(self):
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "show_invoice_lessons.html")

    def test_not_logged_in_get_request(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_page_shows_lessons_associated_to_invoice(self):
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        for lesson_number in range(self.start_lesson_number, self.end_lesson_number):
            self.assertContains(response, f'Lesson__{lesson_number}')

    def test_only_lessons_belonging_to_invoice_are_shown(self):
        self.client.force_login(self.student)
        for lesson_number in range(self.start_lesson_number, self.end_lesson_number):
            lesson = Lesson.objects.filter(topic=f'Lesson__{lesson_number}').first()
            self.assertEqual(lesson.student, self.student)