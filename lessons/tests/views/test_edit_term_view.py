from django.test import TestCase
from django.urls import reverse
from lessons.forms import TermForm
from lessons.models import Student, LessonRequest, Admin, Term
import datetime
from django.utils import timezone
import pytz

class EditRequestViewTestCase(TestCase):
    """Tests for the edit term view"""

    fixtures = [
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/admin_user.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.student = Student.objects.get(email="johndoe@example.org")
        self.admin = Admin.objects.get(email="student_admin@example.org")

        self.form_input = {
            'name':'Autumn Term',
            'start_date':'2024-10-10',
            'end_date':'2025-10-10',
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

        self.url = reverse('edit_terms', kwargs={'term_id': self.term.id})

    def test_request_url(self):
        self.assertEqual(self.url, f'/admin/terms/edit/{self.term.id}')

    def test_get_request(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_terms.html")
        form = response.context['form']
        self.assertTrue(isinstance(form, TermForm))
        self.assertEqual(form.instance, self.term)

    def test_not_logged_in_get_request(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccessful_update(self):
        self.client.force_login(self.admin)
        #invalid as start date after end date
        self.form_input['start_date'] = "2022-10-10"
        self.form_input['end_date'] = "2020-10-10"
        before = Term.objects.count()
        response = self.client.post(self.url, self.form_input)
        after = Term.objects.count()
        self.assertEqual(before, after)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_terms.html")
        form = response.context['form']
        self.assertTrue(isinstance(form, TermForm))
        self.assertTrue(form.is_bound)

    def test_successful_update(self):
        self.client.force_login(self.admin)
        before = Term.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after = Term.objects.count()
        self.assertEqual(before, after)
        response_url = reverse('admin_terms')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_terms.html')

    def test_student_reject_access(self):
        self.client.login(username=self.student.email, password='Password123')
        redirect_url = reverse("student_home")
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
