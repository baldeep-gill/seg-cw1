from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import Term
import datetime
import pytz


class TermTestCase(TestCase):
    """Unit tests for term model"""

    fixtures = [
        'lessons/tests/fixtures/default_term.json',
        'lessons/tests/fixtures/other_terms.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()

        self.term = Term.objects.get(name="Summer Term")
        self.other_term = Term.objects.get(name="Winter Term")


    def _assert_valid_term(self):
        try:
            self.term.full_clean()
        except ValidationError:
            self.fail("Test term should be valid")

    def _assert_invalid_term(self):
        with self.assertRaises(ValidationError):
            self.term.full_clean()


    def test_valid_term(self):
        self._assert_valid_term()

    """---TEST NAME FIELD---"""

    def test_name_cant_be_blank(self):
        self.term.name = None
        self._assert_invalid_term()

    def test_number_characters_in_name_can_be_50(self):
        self.term.name = "x" * 50
        self._assert_valid_term()

    def test_number_characters_in_name_cannot_be_51(self):
        self.term.name = "x" * 51
        self._assert_invalid_term()

    def test_name_must_be_unqiue(self):
        self.term.name = self.other_term.name
        self._assert_invalid_term()

    """---TEST START_DATE FIELD---"""

    def test_start_date_cant_be_blank(self):
        self.term.start_date = None
        self._assert_invalid_term()

    def test_start_date_if_of_type_datetime(self):
        self.assertIsInstance(self.term.start_date,datetime.datetime)

    """---TEST END_DATE FIELD---"""

    def test_end_date_cant_be_blank(self):
        self.term.end_date = None
        self._assert_invalid_term()

    def test_end_date_if_of_type_datetime(self):
        self.assertIsInstance(self.term.end_date,datetime.datetime)



