from django.test import TestCase
from lessons.models import Student,Lesson
from lessons.forms import BookLessonRequestForm
import datetime
import pytz

class BookLessonRequestFromTestCase(TestCase):
    """Unit tests for lesson request form"""

    fixtures = [
        'lessons/tests/fixtures/default_student.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.student = Student.objects.get(email="johndoe@example.org")
        self.form_input = {
            "duration": 60,
            "topic": "piano",
            "teacher": "Mr Bob",
            "start_date": "2022-10-21",
            "day": "Wednesday",
            "time": "12:00",
            "interval_between_lessons": 1,
            "number_of_lessons": 6,

        }

    def test_form_contains_fields(self):
        form = BookLessonRequestForm()
        self.assertIn("duration", form.fields)
        self.assertIn("topic", form.fields)
        self.assertIn("teacher", form.fields)
        self.assertIn("start_date", form.fields)
        self.assertIn("day", form.fields)
        self.assertIn("time", form.fields)
        self.assertIn("interval_between_lessons", form.fields)
        self.assertIn("number_of_lessons", form.fields)

    def test_accept_valid_input(self):
        form = BookLessonRequestForm(data = self.form_input)
        self.assertTrue(form.is_valid())


    """---TEST DURATION INPUT---"""
    def test_reject_blank_duration(self):
        self.form_input['duration'] = ''
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_duration_greater_than_120(self):
        self.form_input['duration'] = 121
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_accept_duration_120(self):
        self.form_input['duration'] = 120
        form = BookLessonRequestForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_reject_duration_less_than_30(self):
        self.form_input['duration'] = 29
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_accept_duration_30(self):
        self.form_input['duration'] = 30
        form = BookLessonRequestForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    """---TEST TOPIC INPUT---"""

    def test_reject_blank_topic(self):
        self.form_input['topic'] = ''
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_topic_length_greater_than_50(self):
        self.form_input['topic'] = 'x' * 51
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_accept_topic_length_50(self):
        self.form_input['topic'] = 'x' * 50
        form = BookLessonRequestForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    """---TEST TEACHER INPUT---"""
    def test_reject_blank_teacher(self):
        self.form_input['teacher'] = ''
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_teacher_length_greater_than_50(self):
        self.form_input['teacher'] = 'x' * 51
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_accept_teacher_length_50(self):
        self.form_input['teacher'] = 'x' * 50
        form = BookLessonRequestForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    """---TEST START_DATE INPUT---"""
    def test_reject_blank_start_date(self):
        self.form_input['start_date'] = ''
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_date_not_in_correct_form(self):
        incorrect_forms = ['20221221','2022,12,22','12th December 2022']
        for incorrect_form in incorrect_forms:
            self.form_input['start_date'] = incorrect_form
            form = BookLessonRequestForm(data = self.form_input)
            self.assertFalse(form.is_valid())

    def test_accept_date_in_correct_form(self):
        correct_forms = ['2022-12-21','2013-6-4','2013-06-04']
        for correct_form in correct_forms:
            self.form_input['start_date'] = correct_form
            form = BookLessonRequestForm(data = self.form_input)
            self.assertTrue(form.is_valid())

    def test_reject_year_not_in_suitable_range(self):
        self.form_input['start_date'] = '20022-10-22'
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_month_not_in_correct_range(self):
        self.form_input['start_date'] = '20022-13-22'
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_day_not_in_correct_range(self):
        self.form_input['start_date'] = '20022-10-40'
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())


    """---TEST DAY INPUT---"""
    def test_reject_blank_day(self):
        self.form_input['day'] = ''
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_non_day_input(self):
        self.form_input['day'] = 'non day input'
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_non_capitalised_day_input(self):
        self.form_input['day'] = 'tuesday'
        form = BookLessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_accept_all_days_of_the_week(self):
        days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        for day in days:
            self.form_input['day'] = day
            form = BookLessonRequestForm(data=self.form_input)
            self.assertTrue(form.is_valid())

    """---TEST TIME INPUT---"""
    def test_reject_blank_time(self):
        self.form_input['time'] = ''
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_time_not_in_correct_form(self):
        incorrect_forms = ['1200','3am','4PM']
        for incorrect_form in incorrect_forms:
            self.form_input['time'] = incorrect_form
            form = BookLessonRequestForm(data = self.form_input)
            self.assertFalse(form.is_valid())

    def test_accept_time_in_correct_form(self):
        correct_forms = ['12:00','03:00','16:00','00:00']
        for correct_form in correct_forms:
            self.form_input['time'] = correct_form
            form = BookLessonRequestForm(data = self.form_input)
            self.assertTrue(form.is_valid())

    """---TEST INTERVAL_BETWEEN_LESSONS INPUT---"""
    def test_reject_blank_interval(self):
        self.form_input['interval_between_lessons'] = ''
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_negative_interval(self):
        self.form_input['interval_between_lessons'] = -1
        form = BookLessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_zero_interval(self):
        self.form_input['interval_between_lessons'] = 0
        form = BookLessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_accept_a_range_of_positive_intervals(self):
        positives = [1,3,5]
        for number in positives:
            self.form_input['number_of_lessons'] = number
            form = BookLessonRequestForm(data=self.form_input)
            self.assertTrue(form.is_valid())

    """---TEST NUMBER_OF_LESSONS INPUT---"""

    def test_reject_blank_lesson_num(self):
        self.form_input['number_of_lessons'] = ''
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_negative_lesson_num(self):
        self.form_input['number_of_lessons'] = -1
        form = BookLessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_zero_lesson_num(self):
        self.form_input['number_of_lessons'] = 0
        form = BookLessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_accept_a_range_of_positive_lesson_nums(self):
        positives = [1,10,50]
        for number in positives:
            self.form_input['number_of_lessons'] = number
            form = BookLessonRequestForm(data=self.form_input)
            self.assertTrue(form.is_valid())







