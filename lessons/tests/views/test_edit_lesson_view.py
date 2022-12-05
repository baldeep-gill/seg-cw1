from django.test import TestCase
from django.urls import reverse
from lessons.forms import EditLessonForm
from lessons.models import Student, Admin, Lesson, Invoice
import datetime

class EditLessonViewTestCase(TestCase):
    """Tests for the edit lesson view"""

    fixtures = [
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/admin_user.json',
        'lessons/tests/fixtures/default_invoice.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.student = Student.objects.get(email="johndoe@example.org")
        self.admin = Admin.objects.get(email="student_admin@example.org")
        
        self.lesson = Lesson(
            student = Student.objects.get(email="johndoe@example.org"),
            invoice = Invoice.objects.get(invoice_number=100),
            date = "2022-12-03 12:00:00Z",
            duration = 1,
            topic = "Drums",
            teacher = "Mr Jim"
        )
        self.lesson.save()

        self.form_input = {
            "date": "2023-12-03 12:00:00Z",
            "duration": 60,
            "topic": "Piano",
            "teacher": "Mr Bob"
        }

        self.url = reverse('edit_lessons', kwargs={'lesson_id': self.lesson.id})
    
    def test_lesson_url(self):
        self.assertEqual(self.url, f'/admin/lessons/edit/{self.lesson.id}')

    def test_reject_student_access(self):
        self.client.force_login(self.student)
        redirect_url = reverse("student_home")
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_get_lesson(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_lessons.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditLessonForm))
        self.assertEqual(form.instance, self.lesson)
    
    def test_get_invalid_lesson(self):
        self.client.force_login(self.admin)
        url = reverse('edit_lessons', kwargs={'lesson_id': 9999})
        redirect_url = reverse('admin_lessons')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_not_logged_in_get_lesson(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_lesson_edit(self):
        self.client.force_login(self.admin)
        self.form_input['duration'] = 65
        before = Lesson.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after = Lesson.objects.count()
        self.assertEqual(before, after)
        response_url = reverse('admin_lessons')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_lesson_list.html')
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.date, datetime.datetime(2023, 12, 3, 12, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(self.lesson.duration, 65)
        self.assertEqual(self.lesson.topic, "Piano")
        self.assertEqual(self.lesson.teacher, "Mr Bob")
    
    def test_unsuccessful_lesson_edit(self):
        self.client.force_login(self.admin)
        self.form_input['duration'] = "sixty"
        before = Lesson.objects.count()
        response = self.client.post(self.url, self.form_input)
        after = Lesson.objects.count()
        self.assertEqual(before, after)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_lessons.html")
        form = response.context['form']
        self.assertTrue(isinstance(form, EditLessonForm))
        self.assertTrue(form.is_bound)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.date, datetime.datetime(2022, 12, 3, 12, 0, tzinfo=datetime.timezone.utc))
        self.assertEqual(self.lesson.duration, 1)
        self.assertEqual(self.lesson.topic, "Drums")
        self.assertEqual(self.lesson.teacher, "Mr Jim")
        
    def test_not_logged_in_get_lesson(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
