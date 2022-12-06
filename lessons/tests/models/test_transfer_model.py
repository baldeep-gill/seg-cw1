from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import Student, Admin, Transfer, Invoice
import datetime
import pytz
from django.utils import timezone
from  lessons.helpers import find_next_available_transfer_id

class TransferTestCase(TestCase):
    """Unit tests for transfer model"""
    
    fixtures = [
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/admin_user.json',
        'lessons/tests/fixtures/default_invoice.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        # Student who lesson is for
        self.student = Student.objects.get(email="johndoe@example.org")
        self.admin = Admin.objects.get(email="student_admin@example.org")
        self.invoice = Invoice.objects.get(invoice_number=100)

        self.transfer = Transfer(
            date_received = timezone.now(),
            transfer_id = find_next_available_transfer_id(),
            verifier = self.admin,
            invoice = self.invoice,
            amount_received = self.invoice.price
        )


    def _assert_valid_transfer(self):
        try:
            self.transfer.full_clean()
        except ValidationError:
            self.fail("Test transfer should be valid")

    def _assert_invalid_transfer(self):
        with self.assertRaises(ValidationError):
            self.transfer.full_clean()


    def test_valid_transfer(self):
        self._assert_valid_transfer()

    """---TEST VERIFIER FIELD---"""

    def test_student_cant_be_blank(self):
        self.transfer.verifier = None
        self._assert_invalid_transfer()


    """---TEST DATE FIELD---"""

    def test_date_cant_be_blank(self):
        self.transfer.date_received = None
        self._assert_invalid_transfer()

    def test_date_cant_be_in_the_future(self):
        self.transfer.date_received = timezone.now() + datetime.timedelta(days=1)
        self._assert_invalid_transfer()

    def test_date_can_be_in_the_past(self):
        self.transfer.date_received = timezone.now() - datetime.timedelta(days=3)
        self._assert_valid_transfer()

    """---TEST VERIFIERS FIELD---"""

    def test_verifier_cant_be_blank(self):
        self.transfer.verifier = None
        self._assert_invalid_transfer()

    """---TEST transfer FIELD---"""

    def test_transfer_cant_be_blank(self):
        self.transfer.invoice = None
        self._assert_invalid_transfer()

    """---TEST transfer FIELD---"""

    def test_amount_cant_be_blank(self):
        self.transfer.amount_received = None
        self._assert_invalid_transfer()

    


   
















