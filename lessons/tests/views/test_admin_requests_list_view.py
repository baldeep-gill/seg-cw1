from django.test import TestCase
from django.urls import reverse
from lessons.models import Student, Admin
from lessons.tests.helpers import create_requests
from lessons.management.commands.seed import Command

class ShowAdminRequestListViewTestCase(TestCase):
    """Tests for the admin-only lesson requests list view"""

    fixtures = ['lessons/tests/fixtures/default_student.json', 'lessons/tests/fixtures/admin_user.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.url = reverse('admin_requests')
        self.student = Student.objects.get(email="johndoe@example.org")
        self.admin = Admin.objects.get(email="student_admin@example.org")

    def test_request_url(self):
        self.assertEqual(self.url, '/admin/requests')

    def test_get_request_as_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_lesson_list.html")
    
    def test_get_request_as_student(self):
        self.client.force_login(self.student)
        redirect_url = reverse("student_home")
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_not_logged_in_get_request(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)