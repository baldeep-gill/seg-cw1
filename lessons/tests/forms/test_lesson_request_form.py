from django.test import TestCase
from lessons.models import Student
from lessons.forms import LessonRequestForm

class LessonRequestFromTestCase(TestCase):
    """Unit tests for lesson request form"""

    fixtures = [
        'lessons/tests/fixtures/default_student.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.student = Student.objects.get(email="johndoe@example.org")
        self.form_input = {
            "availability": "Monday",
            "lessonNum": 3,
            "interval": 1,
            "duration": 60,
            "topic": "piano",
            "teacher": "Mr Bob"
        }

    def test_form_contains_fields(self):
        form = LessonRequestForm()
        self.assertIn("availability", form.fields)
        self.assertIn("lessonNum", form.fields)
        self.assertIn("interval", form.fields)
        self.assertIn("duration", form.fields)
        self.assertIn("topic", form.fields)
        self.assertIn("teacher", form.fields)

    def test_accept_valid_input(self):
        form = LessonRequestForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_reject_blank_availability(self):
        self.form_input['availability'] = ''
        form = LessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_blank_lesson_num(self):
        self.form_input['lessonNum'] = ''
        form = LessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_blank_interval(self):
        self.form_input['interval'] = ''
        form = LessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_blank_duration(self):
        self.form_input['duration'] = ''
        form = LessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_blank_topic(self):
        self.form_input['topic'] = ''
        form = LessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_accept_blank_teacher(self):
        self.form_input['teacher'] = ''
        form = LessonRequestForm(data = self.form_input)
        self.assertTrue(form.is_valid()) 