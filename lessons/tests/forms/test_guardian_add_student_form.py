from django.test import TestCase
from lessons.models import Student, LessonRequest, Guardian, GuardianProfile
from lessons.forms import GuradianAddStudent

class BookForStudentForm(TestCase):
    """Unit tests for lesson request edit form"""

    fixtures = [
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/guardian_user.json',
    ]

    def setUp(self):
        self.student = Student.students.get(email="johndoe@example.org")
        self.guardian = Guardian.guardians.get(email="main.man@example.org")
        
        self.form_input = {
            "student_first_name": self.student.first_name,
            "student_last_name": self.student.last_name,
            "student_email": self.student.email,
        }

    def test_form_contains_fields(self):
        form = GuradianAddStudent()
        self.assertIn("student_first_name", form.fields)
        self.assertIn("student_last_name", form.fields)
        self.assertIn("student_email", form.fields)

    def test_reject_blank_student_first_name(self):
        self.form_input['student_first_name'] = ''
        form = GuradianAddStudent(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_accept_form_with_correct_inputs(self):
        form = GuradianAddStudent(data=self.form_input)
        self.assertTrue(form.is_valid())
        
