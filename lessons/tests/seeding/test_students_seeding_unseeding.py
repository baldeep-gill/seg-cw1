#TODO Uncomment this when want to test seeder

# from django.test import TestCase
# from lessons.models import Student, Admin, User, StudentProfile
# from django.core.management import call_command
#
# # Create your tests here.
#
# class UserModeTestCase(TestCase):
#
#     def test_seeding_creates_expected_number_of_users(self):
#         call_command('seed')
#         # the seeder creates 100 student users using Faker
#         # as well as 1 user with specified information (John Doe)
#         student_count = Student.students.count()
#         admins_count = Admin.admins.count()
#         user_count = User.objects.count()
#         student_profile_count = StudentProfile.objects.count()
#         self.assertEqual(student_count, 100)
#         self.assertEqual(admins_count, 100)
#         self.assertEqual(student_profile_count, 100)
#         self.assertEqual(user_count, 200)
#
#     def test_unseeding_clears_student_users(self):
#         call_command('unseed')
#         student_count = Student.students.count()
#         admins_count = Admin.admins.count()
#         student_profile_count = StudentProfile.objects.count()
#         user_count = User.objects.count()
#         self.assertEqual(student_count, 0)
#         self.assertEqual(admins_count, 0)
#         self.assertEqual(student_profile_count, 0)
#         self.assertEqual(user_count, 0)