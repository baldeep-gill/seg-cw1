from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from lessons.forms import StudentSignUpForm
from lessons.models import Student
from lessons.tests.helpers import LogInTester
from lessons.helpers import find_next_available_student_number

class SignUpViewTestCase(TestCase,LogInTester):
    """ Tests of the student sign up view"""

    def setUp(self):
        self.url = reverse('student_sign_up')
        self.form_input = {
            "first_name" : "John",
            "last_name" : "Doe",
            "email" : "johndoe@example.org",
            "new_password" : "Password123",
            "password_confirmation" : "Password123"
        }

    def test_sign_up_url(self):
        self.assertEqual(reverse('student_sign_up'),'/student_sign_up/')


    def test_get_sign_up(self):
        url = reverse('student_sign_up')
        response = self.client.get(url)
        #response should include status code of 200 if page rendered successfully
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'student_sign_up.html')

        form = response.context['form']
        self.assertTrue(isinstance(form, StudentSignUpForm))
        self.assertFalse(form.is_bound)


    def test_unsuccessful_sign_up(self):
        self.form_input['email'] = 'bad-email'
        response = self.client.post(self.url,self.form_input)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_sign_up.html')

        form = response.context['form']
        self.assertTrue(isinstance(form, StudentSignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())


    def test_successful_sign_up(self):
        """Students should be redirected to home page after successful sign up
        They should not be logged in by the system after signing up"""

        before_count = Student.objects.count()
        response = self.client.post(self.url,self.form_input,follow=True)
        after_count = Student.objects.count()
        self.assertEqual(after_count,before_count+1)

        response_url = reverse('home')
        self.assertRedirects(response, response_url,status_code=302,target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

        student = Student.objects.get(email='johndoe@example.org')
        correct_student_number = find_next_available_student_number() - 1
        self.assertEqual(student.first_name, 'John')
        self.assertEqual(student.last_name, 'Doe')
        self.assertEqual(student.email, 'johndoe@example.org')
        self.assertEqual(student.student_number, correct_student_number)
        self.assertEqual(student.username, 'JohnDoe'+f'{correct_student_number}')
        is_password_correct = check_password('Password123', student.password)
        self.assertTrue(is_password_correct)

        self.assertFalse(self._is_logged_in())




