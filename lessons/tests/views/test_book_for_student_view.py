from django.test import TestCase
from django.urls import reverse
from lessons.models import Student, Guardian, GuardianProfile
from lessons.forms import LessonRequest, GuradianBookStudent

class ShowAdminRequestListViewTestCase(TestCase):
    """Tests for the admin-only lesson requests list view"""
    
    fixtures = [
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/other_students.json',
        'lessons/tests/fixtures/guardian_user.json',
    ]

    def setUp(self):
        self.student = Student.students.get(email="johndoe@example.org")
        self.other_student = Student.students.get(email="janedoe@example.org")
        self.guardian = Guardian.guardians.get(email="main.man@example.org")
        self.options = (self.student.email, self.student.first_name)
        
        self.url = reverse('book_for_student')
        
        self.form_input = {
            "availability": "Monday",
            "lessonNum": 2,
            "interval": 1,
            "duration": 60,
            "topic": "piano",
            "teacher": "Mr Bob",
            "students": self.student.email
        }

    def test_request_url(self):
        self.assertEqual(self.url, '/guardian/book/')

    def test_not_logged_in_get_request(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_add_student(self):
        self.client.login(username=self.guardian.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'guardian_book_for_student.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, GuradianBookStudent))
    
    def test_user_can_book_for_students(self):
        GuardianProfile.objects.create(user=self.guardian, student_first_name=self.student.first_name, student_last_name=self.student.last_name, student_email=self.student.email)
        self.client.login(username=self.guardian.email, password='Password123')
        count_before = LessonRequest.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('guardian_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'guardian_home.html')
        count_after = LessonRequest.objects.count()
        self.assertEqual(count_after, count_before+1)

    def test_user_can_not_book_for_students_with_invalid_data(self):
        self.client.login(username=self.guardian.email, password='Password123')
        count_before = GuardianProfile.objects.count()
        self.form_input['availability'] = ''
        response = self.client.post(self.url, self.form_input, follow=True)
        count_after = GuardianProfile.objects.count()
        self.assertEqual(count_after, count_before)

    def test_user_can_only_see_his_students(self):
        GuardianProfile.objects.create(user=self.guardian, student_first_name=self.student.first_name, student_last_name=self.student.last_name, student_email=self.student.email)
        self.client.login(username=self.guardian.email, password='Password123')
        response = self.client.get(self.url)
        form = response.context['form']
        self.assertEqual(len(form.fields['students'].choices), 1)

    def test_user_can_not_book_if_they_do_not_have_students(self):
        self.client.login(username=self.guardian.email, password='Password123')
        response = self.client.get(self.url)
        response = self.client.get(self.url)
        self.assertContains(response, 'You have 0 students that you are a guardian of')
    