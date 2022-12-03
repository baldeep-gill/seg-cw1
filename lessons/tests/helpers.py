from lessons.models import LessonRequest, Lesson, Invoice
from django.urls import reverse
from lessons.helpers import find_next_available_invoice_number_for_student
import datetime
import pytz

# for future use
class LogInTester:
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()

def create_requests(author, from_count, to_count):
    """Create unique numbered requests for testing purposes."""
    for count in range(from_count, to_count):
        text = f'Request__{count}'
        request = LessonRequest(
            author=author, 
            availability = text,
            lessonNum = 1,
            interval = 1,
            duration = 60,
            topic = "temp",
            teacher = "temp"
        )
        request.save()

def create_invoices(student, from_count, to_count):
    """Create unique numbered invoices for testing purposes
    Creates Invoices only, no lessons"""
    date = datetime.datetime(year=2022,month=10,day=10,tzinfo=pytz.UTC)
    for count in range(from_count, to_count):
        invoice = Invoice(
            student=student,
            date=date.__str__(),
            invoice_number=count
        )
        invoice.save()

def create_lesson_set(student, from_count, to_count):
    f"""Creates a lesson set with an asscociated invoice
    Lessons are for passed in student
    Can identify a lesson with its topic and count number
    Can identify an invoice as its invoice number will equal to {from_count}
    """
    date = datetime.datetime(year=2022,month=10,day=10,tzinfo=pytz.UTC)
    invoice = Invoice(
        student=student,
        date=date.__str__(),
        invoice_number=from_count
    )
    invoice.save()
    for count in range(from_count, to_count):
        lesson = Lesson(
            student=student,
            invoice=invoice,
            date=date.__str__(),
            duration = 60,
            topic = f'Lesson__{count}',
            teacher='temp'
        )
        lesson.save()


def reverse_with_next(url_name, next_url):
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url