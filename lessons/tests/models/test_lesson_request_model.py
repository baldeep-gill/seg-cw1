from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import LessonRequest, Student

class LessonRequestTestCase(TestCase):
    """Unit tests for lesson request model"""
    
    fixtures = [
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/default_lesson_request.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.student = Student.objects.get(email="johndoe@example.org")
        self.lessonRequest = LessonRequest.objects.get(author=1)

    def _assert_valid_request(self):
        try:
            self.lessonRequest.full_clean()
        except ValidationError:
            self.fail("Test request should be valid")

    def _assert_invalid_request(self):
        with self.assertRaises(ValidationError):
            self.lessonRequest.full_clean()


    def test_valid_request(self):
        self._assert_valid_request()

    def test_null_user(self):
        self.lessonRequest.author = None
        self._assert_invalid_request()

    def test_one_lesson(self):
        self.lessonRequest.lessonNum = 1
        self._assert_valid_request()

    def test_no_lessons(self):
        self.lessonRequest.lessonNum = 0
        self._assert_invalid_request()

    def test_one_week_interval(self):
        self.lessonRequest.interval = 1
        self._assert_valid_request()

    def test_zero_week_interval(self):
        self.lessonRequest.interval = 0
        self._assert_invalid_request()

    def test_30_min_lesson(self):
        self.lessonRequest.duration = 30
        self._assert_valid_request()

    def test_15_min_lesson(self):
        self.lessonRequest.duration = 15
        self._assert_invalid_request()

    def test_2_hour_lesson(self):
        self.lessonRequest.duration = 120
        self._assert_valid_request()

    def test_3_hour_lesson(self):
        self.lessonRequest.duration = 180
        self._assert_invalid_request()

    def test_teacher_can_be_blank(self):
        self.lessonRequest.teacher = ''
        self._assert_valid_request()
