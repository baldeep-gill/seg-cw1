from django.test import TestCase
from lessons.models import Student
from django.core.management import call_command

# Create your tests here.

class UserModeTestCase(TestCase):

    def test_seeding_creates_expected_number_of_users(self):
        call_command('seed')
        # the seeder creates 100 student users using Faker
        # as well as 1 user with specified information (John Doe)
        student_count = Student.objects.count()
        self.assertEqual(student_count, 101)

    def test_unseeding_clears_student_users(self):
        call_command('unseed')
        student_count = Student.objects.count()
        self.assertEqual(student_count, 0)