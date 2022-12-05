from django.test import TestCase
from lessons.models import Student, Lesson, Invoice
from lessons.forms import EditLessonForm

class EditLessonFormTestCase(TestCase):
    """Unit tests for lesson edit form"""

    fixtures = [
        'lessons/tests/fixtures/admin_user.json',
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/default_invoice.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.student = Student.objects.get(email="johndoe@example.org")
        self.form_input = {
            "date": "2023-12-03 12:00:00Z",
            "duration": 60,
            "topic": "Piano",
            "teacher": "Mr Bob"
        }

        self.lesson = Lesson(
            student = Student.objects.get(email="johndoe@example.org"),
            invoice = Invoice.objects.get(invoice_number=100),
            date = "2022-12-03 12:00:00Z",
            duration = 1,
            topic = "Drums",
            teacher = "Mr Jim"
        )

    def test_lesson_edit(self):
        self.form_input['duration'] = 61
        form = EditLessonForm(instance=self.lesson, data=self.form_input)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(61, self.lesson.duration)

    def test_form_contains_fields(self):
        form = EditLessonForm()
        self.assertIn("date", form.fields)
        self.assertIn("duration", form.fields)
        self.assertIn("topic", form.fields)
        self.assertIn("teacher", form.fields)

    def test_accept_valid_input(self):
        form = EditLessonForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_reject_blank_date(self):
        self.form_input['date'] = ""
        form = EditLessonForm(data = self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_reject_blank_duration(self):
        self.form_input['duration'] = ""
        form = EditLessonForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_blank_topic(self):
        self.form_input['topic'] = ""
        form = EditLessonForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_blank_teacher(self):
        self.form_input['teacher'] = ""
        form = EditLessonForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    