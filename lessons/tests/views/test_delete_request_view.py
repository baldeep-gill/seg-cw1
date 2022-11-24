from django.test import TestCase
from django.urls import reverse
from lessons.forms import EditForm
from lessons.models import Student, LessonRequest

class DeleteRequestViewTestCase(TestCase):
    """Tests for the delete request view"""

    fixtures = ['lessons/tests/fixtures/default_student.json']

    def setUp(self):
        super(TestCase, self).setUp()
        self.student = Student.objects.get(email="johndoe@example.org")
        
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

    # def test_not_logged_in_get_request(self):
    #     redirect_url = reverse("log_in") + f"?next={self.url}"
    #     response = self.client.get(self.url)
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # def test_unsuccessful_update(self):
    #     self.client.force_login(self.student)
    #     self.form_input['lessonNum'] = "two"
    #     before = LessonRequest.objects.count()
    #     response = self.client.post(self.url, self.form_input)
    #     after = LessonRequest.objects.count()
    #     self.assertEqual(before, after)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "edit_requests.html")
    #     form = response.context['form']
    #     self.assertTrue(isinstance(form, EditForm))
    #     self.assertTrue(form.is_bound)
    #     self.lessonRequest.refresh_from_db()
    #     self.assertEqual(self.lessonRequest.availability, "Monday")
    #     self.assertEqual(self.lessonRequest.lessonNum, 2)
    #     self.assertEqual(self.lessonRequest.interval, 1)
    #     self.assertEqual(self.lessonRequest.duration, 60)
    #     self.assertEqual(self.lessonRequest.topic, "Piano")
    #     self.assertEqual(self.lessonRequest.teacher, "Mr Bob")

    # def test_successful_update(self):
    #     self.client.force_login(self.student)
    #     self.form_input['lessonNum'] = 5
    #     before = LessonRequest.objects.count()
    #     response = self.client.post(self.url, self.form_input, follow=True)
    #     after = LessonRequest.objects.count()
    #     self.assertEqual(before, after)
    #     response_url = reverse('show_requests')
    #     self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, 'show_requests.html')
    #     self.lessonRequest.refresh_from_db()
    #     self.assertEqual(self.lessonRequest.availability, "Monday")
    #     self.assertEqual(self.lessonRequest.lessonNum, 5)
    #     self.assertEqual(self.lessonRequest.interval, 1)
    #     self.assertEqual(self.lessonRequest.duration, 60)
    #     self.assertEqual(self.lessonRequest.topic, "Piano")
    #     self.assertEqual(self.lessonRequest.teacher, "Mr Bob")