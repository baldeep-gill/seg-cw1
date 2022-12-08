from django.core.management.base import BaseCommand, CommandError
from lessons.models import User, LessonRequest, Term, Lesson, Transfer,  Invoice

class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        LessonRequest.objects.all().delete()
        Lesson.objects.all().delete()
        Transfer.objects.all().delete()
        Invoice.objects.all().delete()
        Term.objects.filter(name__in=['Term one','Term two','Term three','Term four','Term five','Term six']).delete()

