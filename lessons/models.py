"""Models in the lessons app."""

from django.db import models
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar

# Create your models here.
class Student(AbstractUser):
    """User model used for student"""
    #student number = student unique reference number
    student_number = models.IntegerField(unique=True,blank=False)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)

    def full_name(self):
        """Return the full name of the student"""
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)