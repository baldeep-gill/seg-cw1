from django.test import TestCase
from lessons.models import Student,Lesson, Term, LessonRequest
from lessons.forms import BookLessonRequestForm
from lessons.helpers import calculate_how_many_lessons_fit_in_given_dates, get_next_term
from django.utils import timezone
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

        # We will create a term date that starts 3 months from now and ends 6 months from now
        # This is so the tests never fail due to becoming outdated
        tdelta = datetime.timedelta(weeks=12)
        start_term_date = datetime.datetime.now(tz=pytz.UTC) + tdelta
        end_term_date = start_term_date + tdelta

        self.term = Term.objects.create(
            name="Summer Term",
            start_date=start_term_date,
            end_date=end_term_date,
        )

        self.form_input = {
            "duration": 60,
            "topic": "piano",
            "teacher": "Mr Bob",
            "term":f"{self.term.name}",
            "start_date": f"{self.term.start_date}",
            "end_date": f"{self.term.end_date}",
            "day": "Wednesday",
            "time": "12:00",
            "interval_between_lessons": 1,
            "number_of_lessons": 6,
        }

        self.lesson_request = LessonRequest.objects.create(
            author=self.student,
            availability='Wednesday',
            lessonNum=10,
            interval=1,
            duration=60,
            topic='Saxophone',
            teacher='Mr Sax'
        )

    def test_form_contains_fields(self):
        form = BookLessonRequestForm()
        self.assertIn("duration", form.fields)
        self.assertIn("topic", form.fields)
        self.assertIn("teacher", form.fields)
        self.assertIn("term", form.fields)
        self.assertIn("start_date", form.fields)
        self.assertIn("end_date", form.fields)
        self.assertIn("day", form.fields)
        self.assertIn("time", form.fields)
        self.assertIn("interval_between_lessons", form.fields)
        self.assertIn("number_of_lessons", form.fields)

    def test_accept_valid_input(self):
        form = BookLessonRequestForm(lesson_request_id=self.lesson_request.id,data = self.form_input)
        self.assertTrue(form.is_valid())


    """---TEST DURATION INPUT---"""
    def test_reject_blank_duration(self):
        self.form_input['duration'] = ''
        form = BookLessonRequestForm(data=self.form_input)
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

    """---TEST TERM INPUT---"""
    def test_reject_blank_term(self):
        self.form_input['term'] = ''
        form = BookLessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_invalid_term_name(self):
        """Testing if input is not the name of any term"""
        self.form_input['term'] = 'THIS IS NOT THE NAME OF ANY TERM'
        form = BookLessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_invalid_outdated_term(self):
        """Testing if input rejects a term that is outdated"""

        # Getting term dates in the past
        tdelta = datetime.timedelta(weeks=12)
        outdated_start_term_date = datetime.datetime.now(tz=pytz.UTC) - (tdelta*2)
        outdated_end_term_date = outdated_start_term_date + tdelta

        Term.objects.create(
            name="Outdated Term",
            start_date=outdated_start_term_date,
            end_date=outdated_end_term_date,
        )

        self.form_input['term'] = 'Outdated Term'
        form = BookLessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())


    """---TEST START_DATE INPUT---"""
    def test_reject_blank_start_date(self):
        self.form_input['start_date'] = ''
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_start_date_not_in_correct_form(self):
        incorrect_forms = ['20221221','2022,12,22','12th December 2022']
        for incorrect_form in incorrect_forms:
            self.form_input['start_date'] = incorrect_form
            form = BookLessonRequestForm(data = self.form_input)
            self.assertFalse(form.is_valid())

    def test_reject_start_year_not_in_suitable_range(self):
        self.form_input['start_date'] = '20022-10-22'
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_start_month_not_in_correct_range(self):
        self.form_input['start_date'] = '20022-13-22'
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_start_day_not_in_correct_range(self):
        self.form_input['start_date'] = '20022-10-40'
        form = BookLessonRequestForm(data = self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_start_date_is_after_end_date(self):
        start_date = self.term.start_date
        end_date = self.term.end_date
        self.form_input['start_date'] = end_date
        self.form_input['end_date'] = start_date
        form = BookLessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    """---TEST END_DATE INPUT---"""

    def test_reject_blank_end_date(self):
        self.form_input['end_date'] = ''
        form = BookLessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_end_date_not_in_correct_form(self):
        incorrect_forms = ['20221221', '2022,12,22', '12th December 2022']
        for incorrect_form in incorrect_forms:
            self.form_input['end_date'] = incorrect_form
            form = BookLessonRequestForm(data=self.form_input)
            self.assertFalse(form.is_valid())

    def test_reject_end_year_not_in_suitable_range(self):
        self.form_input['end_date'] = '20022-10-22'
        form = BookLessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_end_month_not_in_correct_range(self):
        self.form_input['end_date'] = '20022-13-22'
        form = BookLessonRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_reject_end_day_not_in_correct_range(self):
        self.form_input['start_date'] = '20022-10-40'
        form = BookLessonRequestForm(data=self.form_input)
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

    def test_accept_range_of_positive_lesson_nums(self):
        #getting maximum amount of lessons that can fit in self.term
        max = calculate_how_many_lessons_fit_in_given_dates(self.term.start_date,self.term.end_date,50,1,'Monday')
        positives = [1,max]
        for number in positives:
            self.form_input['number_of_lessons'] = number
            form = BookLessonRequestForm(data=self.form_input)
            self.assertTrue(form.is_valid())

    """---TEST AUTO-FILLING FIELDS---"""
    def test_fields_auto_filled_when_request_id_passed_to_form(self):
        form = BookLessonRequestForm(self.lesson_request.id)
        self.assertEqual(form.fields["duration"].initial,60)
        self.assertEqual(form.fields["teacher"].initial,"Mr Sax")
        self.assertEqual(form.fields["topic"].initial,"Saxophone")
        self.assertEqual(form.fields["interval_between_lessons"].initial,1)
        self.assertEqual(form.fields["number_of_lessons"].initial,10)

    def test_request_id_doesnt_need_to_be_passed_in(self):
        form = BookLessonRequestForm()

    def test_term_filled_in_with_closest_upcoming_term(self):
        tdelta = datetime.timedelta(days=1)
        start_date = timezone.now() + tdelta
        end_date = start_date + tdelta
        cloest_term = Term.objects.create(
            name="Closest Term",
            start_date=start_date,
            end_date=end_date,
        )
        form = BookLessonRequestForm()
        self.assertEqual(form.fields["term"].initial,"Closest Term")

    def test_term_filled_in_with_current_upcoming_term(self):
        tdelta = datetime.timedelta(days=1)
        start_date = timezone.now() - tdelta
        end_date = timezone.now() + tdelta
        current_term = Term.objects.create(
            name="Current Term",
            start_date=start_date,
            end_date=end_date,
        )
        form = BookLessonRequestForm()
        self.assertEqual(form.fields["term"].initial, "Current Term")

    def test_start_date_filled_in_with_closest_upcoming_term_start_date(self):
        tdelta = datetime.timedelta(days=1)
        start_date = timezone.now() + tdelta
        end_date = start_date + tdelta
        cloest_term = Term.objects.create(
            name="Closest Term",
            start_date=start_date,
            end_date=end_date,
        )
        form = BookLessonRequestForm()
        self.assertEqual(form.fields["start_date"].initial.timestamp(),cloest_term.start_date.timestamp())

    def test_end_date_filled_in_with_closest_upcoming_term_end_date(self):
        tdelta = datetime.timedelta(days=1)
        start_date = timezone.now() + tdelta
        end_date = start_date + tdelta
        cloest_term = Term.objects.create(
            name="Closest Term",
            start_date=start_date,
            end_date=end_date,
        )
        form = BookLessonRequestForm()
        self.assertEqual(form.fields["end_date"].initial.timestamp(),cloest_term.end_date.timestamp())






