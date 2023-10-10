import datetime

import pytz
from django.test import TestCase
from django.urls import reverse
from lessons.models import Student, Admin, Term
from lessons.forms import TermForm
from lessons.tests.helpers import create_requests
from lessons.management.commands.seed import Command

class AdminTermViewTestCase(TestCase):
    """Tests for the admin-only lesson requests list view"""

    fixtures = ['lessons/tests/fixtures/default_student.json',
                'lessons/tests/fixtures/admin_user.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.url = reverse('admin_terms')
        self.student = Student.objects.get(email="johndoe@example.org")
        self.admin = Admin.objects.get(email="student_admin@example.org")

        self.form_input = {
            'name':'Spring Term',
            'start_date':'2025-10-10',
            'end_date':'2026-10-10',
        }

    def test_request_url(self):
        self.assertEqual(self.url, '/admin/terms')

    def test_get_request_as_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_terms.html")
    
    def test_get_request_as_student(self):
        self.client.login(username=self.student.email, password='Password123')
        redirect_url = reverse("student_home")
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_not_logged_in_get_request(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccessful_term_creation(self):
        self.client.force_login(self.admin)

        #invalid form input as start date before end date
        self.form_input['start_date'] = '2024-10-10'
        self.form_input['end_date'] = '2020-10-10'
        response = self.client.post(self.url, self.form_input)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_terms.html')

        form = response.context['form']
        self.assertTrue(isinstance(form, TermForm))
        self.assertTrue(form.is_bound)

    def test_successful_term_creation(self):
        self.client.force_login(self.admin)
        before_count = Term.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Term.objects.count()
        self.assertEqual(after_count, before_count + 1)

        self.assertTemplateUsed(response, 'admin_terms.html')

        term = Term.objects.get(name='Spring Term')
        self.assertEqual(term.name, 'Spring Term')
        self.assertEqual(term.start_date, datetime.datetime(year=2025,month=10,day=10,tzinfo=pytz.UTC))
        self.assertEqual(term.end_date, datetime.datetime(year=2026,month=10,day=10,tzinfo=pytz.UTC))

