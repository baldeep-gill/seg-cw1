from django.core.exceptions import ValidationError
from django.test import TestCase
from django import forms
from django.contrib.auth.hashers import check_password
from lessons.models import Student
from lessons.forms import StudentSignUpForm
from lessons.helpers import find_next_available_student_number



class StudentSignUpFormTestCase(TestCase):
    """
    Unit tests for student sign up form
    """

    def setUp(self):
        self.form_input = {
            "first_name" : "John",
            "last_name" : "Doe",
            "email" : "johndoe@example.org",
            "new_password" : "Password123",
            "password_confirmation" : "Password123"
        }

    def test_valid_sign_up_form(self):
        form = StudentSignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_needed_fields(self):
        form = StudentSignUpForm()

        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)

        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))

        self.assertIn('new_password', form.fields)
        new_password_widget = form.fields['new_password'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))

        self.assertIn('password_confirmation', form.fields)
        password_confirmation_widget = form.fields['password_confirmation'].widget
        self.assertTrue(isinstance(password_confirmation_widget, forms.PasswordInput))

    def test_form_uses_model_validation(self):
        self.form_input['email'] = 'bademail'
        form = StudentSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = StudentSignUpForm(data=self.form_input)
        before_count = Student.objects.count()
        form.save()
        after_count = Student.objects.count()
        self.assertEqual(after_count,before_count+1)

        student = Student.objects.get(email='johndoe@example.org')
        #the student number should be 1 less than the next available one as student as just been created
        correct_student_number = find_next_available_student_number() - 1
        self.assertEqual(student.first_name, 'John')
        self.assertEqual(student.last_name, 'Doe')
        self.assertEqual(student.email, 'johndoe@example.org')
        self.assertEqual(student.more.student_number, correct_student_number)
        self.assertEqual(student.username, 'JohnDoe'+f'{correct_student_number}')
        is_password_correct = check_password('Password123', student.password)
        self.assertTrue(is_password_correct)


    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = StudentSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = StudentSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'PasswordABC'
        self.form_input['password_confirmation'] = 'PasswordABC'
        form = StudentSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = StudentSignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())
