from django.test import TestCase
from django.urls import reverse
from lessons.forms import BookLessonRequestForm
from lessons.models import Student,Lesson,LessonRequest, Admin
import datetime

class BookLessonRequestViewTestCase(TestCase):
    """Tests for the book lesson request view"""

    fixtures = ['lessons/tests/fixtures/default_student.json',
                'lessons/tests/fixtures/admin_user.json']
    def setUp(self):
        super(TestCase, self).setUp()

        self.student = Student.objects.get(email="johndoe@example.org")
        self.admin = Admin.objects.get(email="student_admin@example.org")

        self.lesson_request = LessonRequest.objects.create(
            author = self.student,
            availability = "Monday",
            lessonNum = 2,
            interval = 1,
            duration = 60,
            topic = "Piano",
            teacher = "Mr Bob"
        )
        self.lesson_request.save()

        self.number_of_lessons_to_generate = 2
        # In python datetime, monday is assigned to value 0
        self.day_of_the_week = ("Monday",0)
        self.start_date = datetime.datetime(2022,10,21).__str__()
        self.book_request_form_input = {
            "duration": 60,
            "topic": "Piano",
            "teacher": "Mr Bob",
            "start_date": "2022-10-21",
            "day": f"{self.day_of_the_week[0]}",
            "time": "12:00",
            "interval_between_lessons": 1,
            "number_of_lessons": f'{self.number_of_lessons_to_generate}',
        }

        self.url = reverse('book_lesson_request', kwargs={'request_id': self.lesson_request.id})


    def test_book_request_url(self):
        self.assertEqual(self.url, f'/admin/book_lesson_request/{self.lesson_request.id}')

    def test_get_request_with_valid_request_id(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "book_lesson_request.html")
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(isinstance(form, BookLessonRequestForm))
        self.assertFalse(form.is_bound)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)


    def test_not_logged_in_get_request(self):
        """If not logged in then get redirected to login screen"""
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_not_admin_get_request(self):
        """If logged in but not an admin then should redirect to student home page"""
        self.client.force_login(self.student)
        redirect_url = reverse("student_home")
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccessful_book_lesson_post(self):
        self.book_request_form_input['interval_between_lessons'] = -1
        self.client.force_login(self.admin)
        response = self.client.post(self.url, self.book_request_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_lesson_request.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookLessonRequestForm))
        self.assertTrue(form.is_bound)

    def test_successful_book_lesson_post(self):
        self.client.force_login(self.admin)
        before_count = Lesson.objects.count()
        response = self.client.post(self.url, self.book_request_form_input)
        after_count = Lesson.objects.count()
        self.assertEqual(after_count,before_count+self.number_of_lessons_to_generate)
        self.assertEqual(response.status_code, 302)

        lessons = Lesson.objects.filter(student=self.student)

        for lesson in lessons:
            self.assertEqual(lesson.student, self.student)
            self.assertEqual(lesson.invoice.student, self.student)
            self.assertEqual(lesson.date.weekday(),self.day_of_the_week[1])
            self.assertEqual(lesson.topic, "Piano")
            self.assertEqual(lesson.teacher, "Mr Bob")






