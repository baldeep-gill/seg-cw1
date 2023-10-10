from django.test import TestCase
from lessons.models import Student, LessonRequest, Guardian, GuardianProfile
from lessons.forms import GuradianBookStudent

class BookForStudentForm(TestCase):
    """Unit tests for lesson request edit form"""

    fixtures = [
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/guardian_user.json',
    ]

    def setUp(self):
        self.student = Student.students.get(email="johndoe@example.org")
        self.guardian = Guardian.guardians.get(email="main.man@example.org")
        GuardianProfile.objects.create(user=self.guardian, student_first_name=self.student.first_name, student_last_name=self.student.last_name, student_email=self.student.email)
        self.options = [self.student.email, self.student.first_name]
        
        self.form_input = {
            "availability": "Monday",
            "lessonNum": 2,
            "interval": 1,
            "duration": 60,
            "topic": "piano",
            "teacher": "Mr Bob",
        }

    def test_form_contains_fields(self):
        form = GuradianBookStudent(options=self.options, data=self.form_input)
        self.assertIn("students", form.fields)
        self.assertIn("availability", form.fields)
        self.assertIn("lessonNum", form.fields)
        self.assertIn("interval", form.fields)
        self.assertIn("duration", form.fields)
        self.assertIn("topic", form.fields)
        self.assertIn("teacher", form.fields)
    
    def test_accept_valid_input(self):
        form = GuradianBookStudent(options=self.options, data=self.form_input)
        self.assertTrue(form.is_bound)
        self.assertEqual(form.fields['students'].choices, self.options)


    def test_reject_blank_availability(self):
        self.form_input['availability'] = ''
        form = GuradianBookStudent(options=self.options, data=self.form_input)
        self.assertFalse(form.is_valid())
