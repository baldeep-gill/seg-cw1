from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import LessonRequest, Student, Lesson, Admin,Invoice
import datetime
import pytz


class LessonTestCase(TestCase):
    """Unit tests for lesson model"""
    
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
        self.lessonRequest = LessonRequest.objects.create(
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
        self.invoice = Invoice.objects.create(
            student = self.student,
            date = datetime.datetime(2022,10,21,tzinfo=pytz.UTC),
            invoice_number=invoice_number,
        )

        # Lesson itself
        self.lesson = Lesson.objects.create(
            student = self.student,
            invoice = self.invoice,
            date = datetime.datetime(2022,12,3,tzinfo=pytz.UTC),
            duration = 60,
            topic = "Piano",
            teacher = "bob",
        )


    def _assert_valid_lesson(self):
        try:
            self.lesson.full_clean()
        except ValidationError:
            self.fail("Test lesson should be valid")

    def _assert_invalid_lesson(self):
        with self.assertRaises(ValidationError):
            self.lesson.full_clean()


    def test_valid_lesson(self):
        self._assert_valid_lesson()

    """---TEST STUDENT FIELD---"""

    def test_student_cant_be_blank(self):
        self.lesson.student = None
        self._assert_invalid_lesson()

    def test_deleting_student_deletes_lesson_as_well(self):
        before_size = Lesson.objects.count()
        self.student.delete()
        after_size = Lesson.objects.count()

        self.assertEqual(before_size,after_size+1)

    """---TEST INVOICE FIELD---"""

    def test_invoice_cant_be_blank(self):
        self.lesson.invoice = None
        self._assert_invalid_lesson()

    def test_deleting_invoice_deletes_lesson_as_well(self):
        before_size = Lesson.objects.count()
        self.invoice.delete()
        after_size = Lesson.objects.count()

        self.assertEqual(before_size,after_size+1)

    """---TEST DATE FIELD---"""

    def test_date_cant_be_blank(self):
        self.lesson.date = None
        self._assert_invalid_lesson()

    def test_date_if_of_type_datetime(self):
        self.assertIsInstance(self.lesson.date,datetime.datetime)

    """---TEST DURATION FIELD---"""

    def test_duration_cant_be_blank(self):
        self.lesson.duration = None
        self._assert_invalid_lesson()

    def test_30_min_lesson_is_valid(self):
        self.lesson.duration = 30
        self._assert_valid_lesson()

    def test_15_min_lesson_is_not_valid(self):
        self.lesson.duration = 15
        self._assert_invalid_lesson()

    def test_2_hour_lesson_is_valid(self):
        self.lesson.duration = 120
        self._assert_valid_lesson()

    def test_3_hour_lesson_is_not_valid(self):
        self.lesson.duration = 180
        self._assert_invalid_lesson()


    """---TEST TOPIC FIELD---"""

    def test_topic_cant_be_blank(self):
        self.lesson.topic = None
        self._assert_invalid_lesson()

    def test_number_characters_in_topic_can_be_50(self):
        self.lesson.topic = "x" * 50
        self._assert_valid_lesson()

    def test_number_characters_in_topic_cannot_be_51(self):
        self.lesson.topic = "x" * 51
        self._assert_invalid_lesson()


    """---TEST TEACHER FIELD---"""

    def test_teacher_cant_be_blank(self):
        self.lesson.teacher = None
        self._assert_invalid_lesson()

    def test_number_characters_in_teacher_can_be_50(self):
        self.lesson.teacher = "x" * 50
        self._assert_valid_lesson()

    def test_number_characters_in_teacher_cannot_be_51(self):
        self.lesson.teacher = "x" * 51
        self._assert_invalid_lesson()











