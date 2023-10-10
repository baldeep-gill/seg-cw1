from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from lessons.forms import LogInForm
from lessons.models import Student, Admin
from lessons.tests.helpers import LogInTester

class LogInViewTestCase(TestCase, LogInTester):
    """Tests for the log in view."""
    fixtures = [
            'lessons/tests/fixtures/default_student.json',
            'lessons/tests/fixtures/admin_user.json'
            ]

    def setUp(self):
        self.url = reverse('log_in')
        self.student = Student.objects.get(email='johndoe@example.org')
        self.admin = Admin.objects.get(email='student_admin@example.org')
    
    def test_log_in_url(self):
        self.assertEqual(self.url,'/log_in/')
    
    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(next)
    
    def test_successful_student_log_in(self):
        form_input = { 'username': 'johndoe@example.org', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('student_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_home.html')

    def test_successful_admin_log_in(self):
        form_input = { 'username': 'student_admin@example.org', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('admin_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_home.html')
    
    def test_get_log_in_redirects_when_student_logged_in(self):
        self.client.login(username=self.student.email, password='Password123')
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('student_home')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_home.html')

    def test_unsuccessful_log_in(self):
        form_input = { 'username': 'johndoe@example.org', 'password': 'WrongPassword123' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_log_in_with_blank_email(self):
        form_input = { 'username': '', 'password': 'Password123' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_log_in_with_blank_password(self):
        form_input = { 'username': 'johndoe@example.org', 'password': '' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_successful_log_in_with_redirect(self):
        redirect_url = reverse('student_home')
        form_input = { 'username': 'johndoe@example.org', 'password': 'Password123', 'next': redirect_url }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_home.html')

    def test_post_log_in_redirects_when_logged_in(self):
        self.client.login(username=self.student.email, password="Password123")
        form_input = { 'username': 'wrongemail@example.org', 'password': 'WrongPassword123' }
        response = self.client.post(self.url, form_input, follow=True)
        redirect_url = reverse('student_home')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_home.html')

    def test_post_log_in_with_incorrect_credentials_and_redirect(self):
        redirect_url = reverse('student_home')
        form_input = { 'username': 'johndoe@example.org', 'password': 'WrongPassword123', 'next': redirect_url }
        response = self.client.post(self.url, form_input)
        next = response.context['next']
        self.assertEqual(next, redirect_url)

    def test_valid_log_in_by_inactive_user(self):
        self.student.is_active = False
        self.student.save()
        form_input = { 'username': 'johndoe@example.org', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
            
            
            

