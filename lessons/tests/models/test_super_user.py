from django.test import TestCase
from lessons.models import Admin, User
from lessons.admin import UserAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib import admin
from django.apps import apps

class UserModelTestCase(TestCase):

    fixtures = [
        'lessons/tests/fixtures/super_user.json',
    ]

    def setUp(self):
        self.site = AdminSite()
        self.super_user = User.objects.get(email="admin@example.org")
        self.admin = UserAdmin(model=Admin, admin_site=self.site)

    def test_admin_model_is_registered(self):
        model = apps.get_model(app_label='lessons', model_name='Admin')
        self.assertTrue(admin.site.is_registered(model))

    def test_user_admin_str(self):
        self.assertEqual(str(self.admin), 'lessons.UserAdmin')

    def test_default_fields(self):
        self.assertEqual(len(self.admin.list_display), 5)