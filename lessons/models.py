from django.db import models

class LessonRequests(models.Model):
    availability = models.CharField(
        blank = False,
        max_length = 280,
    )

    lessonNum = models.IntegerField(
        unique = False,
        blank = False,
    )

    interval = models.IntegerField(
        unique = False,
        blank = False,
    )

    duration = models.IntegerField(
        unique = False,
        blank = False,
    )

    topic = models.CharField(
        blank = False,
        max_length = 50,
    )

    teacher = models.CharField(
        blank = True,
        max_length = 50,
    )