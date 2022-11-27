# TODO Uncomment this when want to test seeder

from django.test import TestCase
from lessons.models import LessonRequest
from lessons.management.commands.seed import Command as Seeder
from django.core.management import call_command

# Create your tests here.

class LessonSeedTestCase(TestCase):

    def test_seeding_creates_expected_number_of_lesson_requests(self):
        seedercommand = Seeder()
        Seeder.seedlessonrequests(seedercommand)
        """Only calls the lesson request seeder command to save time"""
        lesson_request_count = LessonRequest.students.count()
        self.assertEqual(lesson_request_count, 15)

    def test_unseeding_clears_lesson_requests(self):
        call_command('unseed')
        lesson_request_count = LessonRequest.students.count()
        self.assertEqual(lesson_request_count, 0)