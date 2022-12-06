from django.test import TestCase
from django.urls import reverse
from lessons.models import Student, Guardian, GuardianProfile
from lessons.forms import LessonRequest, GuradianAddStudent

class ShowAdminRequestListViewTestCase(TestCase):
    """Tests for the admin-only lesson requests list view"""
    
    fixtures = [
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/guardian_user.json',
    ]

    def setUp(self):
        self.student = Student.students.get(email="johndoe@example.org")
        self.guardian = Guardian.guardians.get(email="main.man@example.org")
        self.url = reverse('add_student')
        self.form_input = {
            "student_first_name": self.student.first_name,
            "student_last_name": self.student.last_name,
            "student_email": self.student.email,
        }

    def test_request_url(self):
        self.assertEqual(self.url, '/guardian/add/')

    def test_not_logged_in_get_request(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_add_student(self):
        self.client.login(username=self.guardian.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'guardian_add_student.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, GuradianAddStudent))
    
    def test_user_can_add_students(self):
        self.client.login(username=self.guardian.email, password='Password123')
        count_before = GuardianProfile.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('guardian_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'guardian_home.html')
        count_after = GuardianProfile.objects.count()
        self.assertEqual(count_after, count_before+1)

    def test_user_can_not_add_students_that_do_not_exist(self):
        self.client.login(username=self.guardian.email, password='Password123')
        count_before = GuardianProfile.objects.count()
        self.form_input['student_email'] = ''
        response = self.client.post(self.url, self.form_input, follow=True)
        count_after = GuardianProfile.objects.count()
        self.assertEqual(count_after, count_before)

    def test_user_can_not_add_duplicate_students(self):
        self.client.login(username=self.guardian.email, password='Password123')
        self.client.post(self.url, self.form_input)
        count_before = GuardianProfile.objects.count()
        self.client.post(self.url, self.form_input)
        count_after = GuardianProfile.objects.count()
        self.assertEqual(count_after, count_before)
