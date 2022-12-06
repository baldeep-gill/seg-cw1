from django.test import TestCase
from django.urls import reverse
from lessons.forms import EditForm
from lessons.models import Student, LessonRequest, Admin, Term
import datetime
from django.utils import timezone

class DeleteTermsViewTestCase(TestCase):
    """Tests for the delete terms view"""

    fixtures = [
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/other_students.json',
        'lessons/tests/fixtures/admin_user.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.student = Student.objects.get(email="johndoe@example.org")
        self.other_student = Student.objects.get(email="janedoe@example.org")
        self.admin = Admin.objects.get(email="student_admin@example.org")

        self.form_input = {
            "availability": "Monday",
            "lessonNum": 2,
            "interval": 1,
            "duration": 60,
            "topic": "Piano",
            "teacher": "Mr Bob"
        }


        # We will create a term date that starts 3 months from now and ends 6 months from now
        # This is so the tests never fail due to becoming outdated
        tdelta = datetime.timedelta(weeks=12)
        start_term_date = timezone.now() + tdelta
        end_term_date = start_term_date + tdelta

        self.term = Term.objects.create(
            name="Summer Term",
            start_date=start_term_date,
            end_date=end_term_date,
        )

        self.url = reverse('delete_terms', kwargs={'term_id': self.term.id})

    def test_term_url(self):
        self.assertEqual(self.url, f'/admin/terms/delete/{self.term.id}')

    def test_get_request(self):
        redirect_url = reverse('admin_terms')
        self.client.force_login(self.admin)
        before = Term.objects.count()
        response = self.client.get(self.url)
        after = Term.objects.count()
        self.assertEqual(after, before-1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_not_logged_in_get_request(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_student_reject_access(self):
        self.client.login(username=self.student.email, password='Password123')
        redirect_url = reverse("student_home")
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)