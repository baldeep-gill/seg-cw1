from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import Student

# Create your tests here.

class UserModeTestCase(TestCase):

    fixtures = [
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/other_students.json',
    ]

    def setUp(self):
        self.student = Student.objects.get(email="johndoe@example.org")


    """
    --FIRST NAME TESTS--
    """
    def test_first_name_cannot_be_blank(self):
        self.student.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_does_not_have_to_be_unique(self):
        second_user = Student.objects.get(email="janedoe@example.org")
        self.student.first_name = second_user.first_name
        self._assert_user_is_valid()

    def test_first_name_can_be_50_characters(self):
        self.student.first_name = 'x' * 50
        self._assert_user_is_valid()

    def test_first_name_cannot_be_over_50_characters(self):
        self.student.first_name ='x' * 51
        self._assert_user_is_invalid()

    """
    --LAST NAME TESTS--
    """
    def test_last_name_cannot_be_blank(self):
        self.student.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_does_not_have_to_be_unique(self):
        second_user = Student.objects.get(email="janedoe@example.org")
        self.student.last_name = second_user.last_name
        self._assert_user_is_valid()

    def test_last_name_can_be_50_characters(self):
        self.student.last_name ='x' * 50
        self._assert_user_is_valid()

    def test_last_name_cannot_be_over_50_characters(self):
        self.student.last_name ='x' * 51
        self._assert_user_is_invalid()

    """
    --EMAIL TESTS--
    """
    def test_email_must_be_unique(self):
        second_user = Student.objects.get(email="janedoe@example.org")
        self.student.email = second_user.email
        self._assert_user_is_invalid()

    def test_email_must_not_be_blank(self):
        self.student.email = ''
        self._assert_user_is_invalid()

    def test_email_needs_at_sign(self):
        self.student.email = 'johndoe.exmaple.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.student.email = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.student.email = 'johndoe@example'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.student.email = 'johndoe@@example.org'
        self._assert_user_is_invalid()

    """
    --STUDENT NUMBER TESTS--
    """
    def test_student_number_must_be_unique(self):
        second_user = Student.objects.get(email="janedoe@example.org")
        self.student.student_number = second_user.student_number
        self._assert_user_is_invalid()

    def test_student_number_must_not_be_blank(self):
        self.student.email = ''
        self._assert_user_is_invalid()


    def _assert_user_is_valid(self):
        """
        Checks if self.student is in a valid state
        """
        try:
            self.student.full_clean()
        except (ValidationError):
            self.fail("Test student should be valid")

    """
    Checks if self.student is not in a valid state
    """
    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.student.full_clean()

