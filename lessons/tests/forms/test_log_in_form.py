from django import forms
from django.test import TestCase
from lessons.forms import LogInForm

class LogInFormTestCase(TestCase):
    """Unit tests for the log in form"""
    def setUp(self):
        self.form_input = {'email': 'johndoe@gmail.com', 'password': 'Password123'}

    def test_form_contains_required_fields(self):
        form = LogInForm()
        self.assertIn('email', form.fields)
        self.assertIn('password', form.fields)
        password_field = form.fields['password']
        self.assertTrue(isinstance(password_field.widget,forms.PasswordInput))

    def test_form_accepts_valid_credentials(self):
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_fields(self):
        self.form_input['email'] = ''
        self.form_input['password'] = ''
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_incorrect_email(self):
        self.form_input['email'] = 'incorrectemail@gmail.com'
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_accepts_incorrect_password(self):
        self.form_input['password'] = 'incorrectpassword'
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid())