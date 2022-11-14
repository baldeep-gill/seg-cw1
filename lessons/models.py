from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class LessonRequest(models.Model):
    """Code to model a students request for a lesson"""

    # Ask which days of the week the student is available for lessons #
    # At some point this should just be some checkboxes next to the days #
    availability = models.CharField(
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