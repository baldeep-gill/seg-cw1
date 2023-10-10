from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import LessonRequest, Student, Lesson, Admin,Invoice
import datetime
import pytz

class InvoiceTestCase(TestCase):
    """Unit tests for invoice model"""
    
    fixtures = [
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/admin_user.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        # Student who lesson is for
        self.student = Student.objects.get(email="johndoe@example.org")
        self.admin = Admin.objects.get(email="student_admin@example.org")

        # Request for lesson
        self.lessonRequest = LessonRequest(
            author = self.student,
            availability = "Monday",
            lessonNum = 2,
            interval = 1,
            duration = 60,
            topic = "Piano",
            teacher = "bob"
        )

        # Invoice which lesson will belong to
        invoice_number = 1
        self.invoice = Invoice(
            student = self.student,
            date = datetime.datetime(2022,10,21,tzinfo=pytz.UTC),
            invoice_number=invoice_number,
        )

        # Lesson itself
        self.lesson = Lesson(
            student = self.student,
            invoice = self.invoice,
            date = datetime.datetime(2022,12,3,tzinfo=pytz.UTC),
            duration = 60,
            topic = "Piano",
            teacher = "bob"
        )

    def _assert_valid_invoice(self):
        try:
            self.invoice.full_clean()
        except ValidationError:
            self.fail("Test invoice should be valid")

    def _assert_invalid_invoice(self):
        with self.assertRaises(ValidationError):
            self.invoice.full_clean()


    def test_valid_invoice(self):
        self._assert_valid_invoice()

    """---TEST STUDENT FIELD---"""

    def test_student_cant_be_blank(self):
        self.invoice.student = None
        self._assert_invalid_invoice()


    """---TEST DATE FIELD---"""

    def test_date_cant_be_blank(self):
        self.invoice.date = None
        self._assert_invalid_invoice()

    """---TEST INVOiCE_NUMBER FIELD---"""

    def test_invoice_number_cant_be_blank(self):
        self.invoice.invoice_number = None
        self._assert_invalid_invoice()


    """---TEST UNIQUE_REFERENCE_NUMBER PROPERTY---"""

    """---TEST LESSONS PROPERTY---"""

    """---TEST PRICE PROPERTY---"""
















