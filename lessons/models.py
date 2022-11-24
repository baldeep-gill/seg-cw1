"""Models in the lessons app."""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy
from libgravatar import Gravatar
from django.core.validators import MinValueValidator, MaxValueValidator

'''The base user that all users inherit'''
class User(AbstractUser):
    '''We will only have two types either a user or an admin (could be extended later on)'''
    class Types(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        STUDENT = "STUDENT", 'Student'
    
    '''defualt role'''
    base_role = Types.ADMIN

    '''Fields that are shared by all users'''
    type = models.CharField(gettext_lazy("Type"), max_length=50, choices=Types.choices, default=base_role)
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
        if not self.id:
            self.type = self.base_role
        return super().save(*args, **kwargs)


'''Student users'''
# manages all students 
class StudentManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.STUDENT)

# A new table to store the student number and extra information about the user later on
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_number = models.IntegerField(unique=True,blank=False)

# Student user
class Student(User):
    base_role = User.Types.STUDENT
    students = StudentManager()
    
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
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.ADMIN)

# Admin user
class Admin(User):
    base_role = User.Types.ADMIN
    admins = AdminManager()
    
    class Meta:
        proxy = True


class LessonRequest(models.Model):
    """Code to model a students request for a lesson"""

    author = models.ForeignKey(
        Student,
        on_delete = models.CASCADE,
        blank = False,
    )

    # Ask which days of the week the student is available for lessons #
    # TODO: figure out how to get bootstrap to create a datetime field input 
    """availability = models.DateTimeField(
        auto_now = False,
        auto_now_add = False,
    )"""

    availability = models.CharField(
        blank = False,
        max_length = 100,
    )

    # How many lessons the student wants #
    lessonNum = models.IntegerField(
        blank = False,
        # If a student is using this service they should be booking at least 1 lesson #
        validators = [
            MinValueValidator(1),
        ],
    )

    # How long (in weeks) should the lessons be spaced out #
    interval = models.IntegerField(
        blank = False,
        default = 1,
        validators = [
            MinValueValidator(1),
        ]
    )

    # Duration of each lesson in minutes #
    duration = models.IntegerField(
        blank = False,
        default = 60,
        validators = [
            # We'll say a lesson should be a minimum of 30 mins, maximum of 2 hours #
            MinValueValidator(30),
            MaxValueValidator(120),
        ],
    )

    # Student should enter a topic #
    topic = models.CharField(
        max_length = 50,
    )

    # Student can enter a teacher if they wish #
    teacher = models.CharField(
        blank = True,
        max_length = 80,
    )


class Invoice(models.Model):
    """Models an invoice for a set of lessons"""

    # Invoice who the student is for
    student = models.ForeignKey(
        Student,
        on_delete = models.CASCADE,
        blank = False,
    )

    # Date and time when invoice was generated
    date = models.DateTimeField(
        blank=False
    )

    # Number of the invoice for the student
    invoice_number = models.IntegerField(
        blank = False,
    )

    # Unique reference number which can be used to identify individual invoices
    # Is of the form student_number-invoice number
    unique_reference_number = models.CharField(
        blank = False,
        unique=True,
        max_length=80
    )

    @property
    def lessons(self):
        return Lesson.objects.filter(invoice=self)

    @property
    def price(self):
        price = 0
        for lesson in self.lessons:
            price += lesson.duration * lesson.price_per_minute
        return price

class Lesson(models.Model):
    """Models a booked lesson for a student"""

    # Lesson who the student is for
    student = models.ForeignKey(
        Student,
        on_delete = models.CASCADE,
        blank = False,
    )

    # Invoice lesson is part of
    invoice = models.ForeignKey(
        Invoice,
        on_delete = models.CASCADE,
        blank = False,
    )

    # Date and time of lesson
    date = models.DateTimeField(
        blank=False
    )

    # Duration of each lesson in minutes
    duration = models.IntegerField(
        blank = False,
        default = 60,
        validators = [
            # We'll say a lesson should be a minimum of 30 mins, maximum of 2 hours #
            MinValueValidator(30),
            MaxValueValidator(120),
        ],
    )

    # What the lesson is about
    topic = models.CharField(
        max_length = 50,
    )

    # Who teaches the lesson
    teacher = models.CharField(
        blank = True,
        max_length = 80,
    )

    @property
    def price_per_minute(self):
        """Returns the cost of this lesson per minute in pounds/£"""
        return 1





