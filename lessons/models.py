"""Models in the lessons app."""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy
from libgravatar import Gravatar

'''The base user that all users inherit'''
class User(AbstractUser):
    '''We will only have two types either a user or an admin (could be extended later on)'''
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        STUDENT = "STUDENT", 'Student'
    
    '''defualt role'''
    base_role = Role.ADMIN

    '''Fields that are shared by all users'''
    type = models.CharField(gettext_lazy("Type"), max_length=50, choices=Role.choices, default=base_role)
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
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
            return super().save(*args, **kwargs)


'''Student users'''
# manages all students 
class StudentManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Role.STUDENT)

    def create_user(self, first_name, last_name, email, password):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=email
        )


        user.set_password(password)
        user.save()
        print("epic success" + first_name + last_name)
        return user

# A new table to store the student number and extra information about the user later on
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_number = models.IntegerField(unique=True,blank=False)

# Student user
class Student(User):
    base_role = User.Role.STUDENT
    objects = StudentManager()
    
    @property
    def more(self):
        '''this refers to the table in the database'''
        return self.studentprofile

    class Meta:
        proxy = True


'''Admin users'''
# manages all Admins 
class AdminManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Role.ADMIN)

# Admin user
class Admin(User):
    base_role = User.Role.ADMIN
    objects = AdminManager()
    class Meta:
        proxy = True
