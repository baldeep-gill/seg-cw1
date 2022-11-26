from django.test import TestCase
from django.urls import reverse
from lessons.forms import EditForm
from lessons.models import Student, LessonRequest, Admin

class DeleteRequestViewTestCase(TestCase):
    """Tests for the delete request view"""

    fixtures = [
        'lessons/tests/fixtures/default_student.json',
        'lessons/tests/fixtures/other_students.json',
        'lessons/tests/fixtures/admin_user.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.student = Student.objects.get(email="johndoe@example.org")
        self.other_student = Student.objects.get(email="janedoe@example.org")
        self.admin = Admin.objects.get(email="student_admin@example.org")
        
        self.lessonRequest = LessonRequest(
            author = self.student,
            availability = "Monday",
            lessonNum = 2,
            interval = 1,
            duration = 60,
            topic = "Piano",
            teacher = "Mr Bob"
        )
        self.lessonRequest.save()

        self.form_input = {
            "availability": "Monday",
            "lessonNum": 2,
            "interval": 1,
            "duration": 60,
            "topic": "Piano",
            "teacher": "Mr Bob"
        }

        self.url = reverse('delete_requests', kwargs={'lesson_id': self.lessonRequest.id})

    def test_request_url(self):
        self.assertEqual(self.url, f'/student/requests/delete/{self.lessonRequest.id}')

    def test_get_request(self):
        redirect_url = reverse('show_requests')
        self.client.force_login(self.student)
        before = LessonRequest.objects.count()
        response = self.client.get(self.url)
        after = LessonRequest.objects.count()
        self.assertEqual(after, before-1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_invalid_request(self):
        """Test if user tries to delete a request that doesn't exist"""
        self.client.force_login(self.student)
        url = reverse('delete_requests', kwargs={'lesson_id': 9999})
        redirect_url = reverse('show_requests')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_not_logged_in_get_request(self):
        redirect_url = reverse("log_in") + f"?next={self.url}"
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_user_cant_delete_other_requests(self):
        """Ensure that users can't delete other users' requests"""
        redirect_url = reverse('home')
        self.client.force_login(self.other_student)
        before = LessonRequest.objects.count()
        response = self.client.get(self.url)
        after = LessonRequest.objects.count()
        self.assertEqual(before, after)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_admin_reject_access(self):
        self.client.force_login(self.admin)
        redirect_url = reverse("admin_home")
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
