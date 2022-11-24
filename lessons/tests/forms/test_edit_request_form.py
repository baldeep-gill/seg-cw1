from django.test import TestCase
from django.core.exceptions import ValidationError
from django import forms
from lessons.models import Student, LessonRequest
from lessons.forms import EditForm

class LessonRequestFromTestCase(TestCase):
    """Unit tests for lesson request edit form"""

    fixtures = [
        'lessons/tests/fixtures/default_student.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.student = Student.objects.get(email="johndoe@example.org")
        self.form_input = {
            "availability": "Monday",
            "lessonNum": 2,
            "interval": 1,
            "duration": 60,
            "topic": "piano",
            "teacher": "Mr Bob"
        }

        self.lessonRequest = LessonRequest(
            author = self.student,
            availability = "Monday",
            lessonNum = 2,
            interval = 1,
            duration = 60,
            topic = "Piano",
            teacher = "bob"
        )

    def test_request_edit(self):
        self.form_input['availability'] = "Tuesday"
        form = EditForm(instance=self.lessonRequest, data=self.form_input)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual("Tuesday", self.lessonRequest.availability)

    def test_form_contains_fields(self):
        form = EditForm()
        self.assertIn("availability", form.fields)
        self.assertIn("lessonNum", form.fields)
        self.assertIn("interval", form.fields)
        self.assertIn("duration", form.fields)
        self.assertIn("topic", form.fields)
        self.assertIn("teacher", form.fields)

    def test_accept_valid_input(self):
        form = EditForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_reject_blank_availability(self):
        self.form_input['availability'] = ''
        form = EditForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_blank_lesson_num(self):
        self.form_input['lessonNum'] = ''
        form = EditForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_blank_interval(self):
        self.form_input['interval'] = ''
        form = EditForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_blank_duration(self):
        self.form_input['duration'] = ''
        form = EditForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_blank_topic(self):
        self.form_input['topic'] = ''
        form = EditForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_accept_blank_teacher(self):
        self.form_input['teacher'] = ''
        form = EditForm(data = self.form_input)
        self.assertTrue(form.is_valid()) 