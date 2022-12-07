from django.core.management.base import BaseCommand, CommandError
from lessons.models import User, LessonRequest, Term

class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        LessonRequest.objects.filter().delete()
        Term.objects.filter(name__in=['Term one','Term two','Term three','Term four','Term five','Term six']).delete()

