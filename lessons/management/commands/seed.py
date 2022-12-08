import pytz
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.utils import timezone
from django.urls import reverse
from faker import Faker
from lessons.models import Student, StudentProfile, Admin, LessonRequest, Term, Guardian, Invoice, Lesson, GuardianProfile, User
from lessons.helpers import find_next_available_student_number, find_next_available_transfer_id, find_next_available_invoice_number_for_student, get_next_given_day_of_week_after_date_given
from datetime import datetime, timedelta
from django.core.management import call_command
import pytz
from django.test import TestCase
from itertools import chain


class Command(BaseCommand, TestCase):
    PASSWORD = "Password123"
    USER_COUNT = 101
    # Includes 100 students, 1 additional admin
    LESSON_REQUEST_COUNT = 30
    # TODO: Use the LESSON_COUNT and USER_COUNT in tests rather than manually written numbers
        
    PROBABILITY_OF_FULFILLED_REQUESTS = 0.8

    FULLY_PAID_PROBABILITY = 0.7
    UNDERPAID_PROBABILITY = 0.3
    OVERPAID_PROBABILITY = 0.2
    UNPAID_PROBABLITY = 0.5
    
    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')


    def handle(self, *args, **options):
        call_command('unseed')

        self.seedusers()
        self.seedterms()

        self.seedunfilfilledlessonrequests()
        self.seedfulfilledrequests()

    
    def seedusers(self):
        self._create_named_client_user(firstname="John", lastname="Doe", email="john.doe@example.org", password="Password123", uname=self._username("John", "Doe"))
        self._create_named_admin_user(firstname="Petra", lastname="Pickles", email="petra.pickles@example.org", password="Password123", uname=self._username("Petra", "Pickles"))

        user_count = 0        
        while user_count < Command.USER_COUNT:
            print(f'Seeding user {user_count}',  end='\r')
            try:
                # seeds 1 admin after 100 students
                seedAdmin = user_count == 100
                self._create_user(isAdmin=seedAdmin)
            except (IntegrityError):
                continue
            user_count += 1
        print('User seeding complete')
        print('Seeded ' + str(User.objects.filter(type="STUDENT").count()) + ' students')
        print('Seeded ' + str(User.objects.filter(type="ADMIN").count()) + ' admins')
        print('Seeded ' + str(User.objects.filter(type="GUARDIAN").count()) + ' guardians')


    def seedterms(self):
        self._create_term('Term one',timezone.datetime(year=2022,month=9,day=1,tzinfo=pytz.UTC),timezone.datetime(year=2022,month=10,day=21,tzinfo=pytz.UTC))
        self._create_term('Term two',timezone.datetime(year=2022,month=10,day=31,tzinfo=pytz.UTC),timezone.datetime(year=2022,month=12,day=16,tzinfo=pytz.UTC))
        self._create_term('Term three',timezone.datetime(year=2023,month=1,day=3,tzinfo=pytz.UTC),timezone.datetime(year=2023,month=2,day=10,tzinfo=pytz.UTC))
        self._create_term('Term four',timezone.datetime(year=2023,month=2,day=20,tzinfo=pytz.UTC),timezone.datetime(year=2023,month=3,day=31,tzinfo=pytz.UTC))
        self._create_term('Term five',timezone.datetime(year=2023,month=4,day=17,tzinfo=pytz.UTC),timezone.datetime(year=2023,month=5,day=26,tzinfo=pytz.UTC))
        self._create_term('Term six',timezone.datetime(year=2023,month=6,day=5,tzinfo=pytz.UTC),timezone.datetime(year=2023,month=7,day=21,tzinfo=pytz.UTC))
        print('term seeding complete')
        print('Seeded ' + str(Term.objects.count()) + ' terms')
        
    def seedunfilfilledlessonrequests(self):
        lesson_count = 0        
        while lesson_count < Command.LESSON_REQUEST_COUNT:
            print(f'Seeding user {lesson_count}',  end='\r')
            try:
                # seeds 1 admin after 100 students
                self._create_lesson()
            except (IntegrityError):
                continue
            lesson_count += 1
        print('lesson request seeding complete')
        print('Seeded ' + str(LessonRequest.objects.count()) + ' requests')

    def book_request(self, student, start_date, interval_between_lessons, number_of_lessons, duration, topic, teacher, day, time):
            #combines the start date picked and the time each day into one dateTime object
            new_date = datetime(start_date.year,start_date.month,start_date.day,time.hour,time.minute,tzinfo=pytz.UTC)
            new_date = get_next_given_day_of_week_after_date_given(new_date,day)

            #generate an invoice for the lessons we will generate
            new_invoice_number = find_next_available_invoice_number_for_student(student)
            invoice = Invoice.objects.create(
                student=student,
                date=datetime.now(tz=pytz.UTC),
                invoice_number=new_invoice_number,
            )
            invoice.save()

            #we will generate a lesson every lesson interval weeks at the time given
            tdelta = timedelta(weeks=interval_between_lessons)
            for i in range(number_of_lessons):
                lesson = Lesson.objects.create(
                    student=student,
                    invoice=invoice,
                    date=new_date,
                    duration=duration,
                    topic=topic,
                    teacher=teacher
                )
                lesson.save()
                new_date = new_date + tdelta
            
            return Lesson.objects.filter(invoice=invoice)
    
    def seedfulfilledrequests(self):
        request_count = 0
        for student in list(chain(Student.objects.all(), Guardian.objects.all())):
            print(f'Seeded {request_count} lessons and invoices',  end='\r')
            if self.faker.random.random() < Command.PROBABILITY_OF_FULFILLED_REQUESTS:
                generated_lessons = self._create_booked_lesson(student)
                request_count += generated_lessons.count()
                for lesson in generated_lessons:
                    random_val = self.faker.random.random()
                    amount = lesson.invoice.price
                    if random_val < Command.OVERPAID_PROBABILITY:
                        amount = random_val*100 + lesson.invoice.price
                    elif random_val < Command.UNDERPAID_PROBABILITY:
                        # Ensures that the value doesn't go below zero
                        amount = max(lesson.invoice.price - random_val*100, random_val*100)
                    elif random_val < Command.UNPAID_PROBABLITY:
                        # Doesn't generate the invoice
                        continue
                    elif random_val < Command.FULLY_PAID_PROBABILITY:
                        # Value remains the invoice price
                        pass
                    self.generate_transfer_for_lesson(amount=amount, lesson=lesson)
        print(f'For {Student.objects.count()} students, generated {Lesson.objects.count()} lessons and {Invoice.objects.count()} invoices')
    
    def _create_booked_lesson(self, client=None):
        if client == None:
            # Random student
            client = Student.objects.order_by('?').first()
        lessonRequest = self._create_lesson()
        # select random term
        term = Term.objects.order_by('?').first()
        # Random day name
        day = self.faker.date_time().strftime("%A")

        lessonNum = self.faker.random.randint(1, 5)
        interval_between_lessons = self.faker.random.randint(1, lessonNum)

        return self.book_request(
            student=client,
            start_date=term.start_date,
            interval_between_lessons=interval_between_lessons,
            number_of_lessons=lessonNum,
            duration=round(self.faker.random.randint(30, 120)),
            time=self.faker.time_object(),
            topic=self.faker.sentence(nb_words=2),
            teacher=self.faker.name(),
            day=day)

        # self.client.post(lessonbookingurl, book_request_form_input)

        

        # transferurl = reverse('approve_transaction', kwargs={'student_id':lessonRequest.student.id, 'invoice_id':invoice.invoice_number})
        # self.client.post(transferurl, confirm_transfer_form_input)

    def generate_transfer_for_lesson(self, amount, lesson):
        invoice = lesson.invoice

        next_transfer_id = find_next_available_transfer_id()

        confirm_transfer_form_input = {
            "date_received": timezone.now(),
            "transfer_id": next_transfer_id,
            "amount_received": amount,
            "verifier": Admin.objects.get(email="petra.pickles@example.org"),
            "invoice": invoice
        }

    def _create_user(self, isAdmin=False):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name, last_name)
        username = self._username(first_name, last_name)
        if(isAdmin): self._create_named_admin_user(first_name, last_name, email, username, Command.PASSWORD)
        else: self._create_named_client_user(first_name, last_name, email, username, Command.PASSWORD)

    def _create_term(self,name,start_date,end_date):
        try:
            new_term = Term.objects.create(
                name=name,
                start_date=start_date,
                end_date=end_date
            )
        except:
            print(f'{name} already in database so we will not duplicate it')


    def _create_lesson(self):
        """Selects a random student user from the database"""
        user = Student.objects.order_by('?').first()
        lessonNum = self.faker.random.randint(1, 5)
        interval = self.faker.random.randint(1, lessonNum)
        duration = round(self.faker.random.randint(30, 120))


        availability_start = self.faker.date_time_this_year(after_now=True, before_now=False)
        availability_range = lessonNum*(interval+1)
        availability = availability_start.strftime("%d/%m/%Y") + " - " + (availability_start + timedelta(days=availability_range*7)).strftime("%d/%m/%Y")

        topic = self.faker.sentence(nb_words=2)
        teacher = self.faker.name()

        lessonRequest = LessonRequest.objects.create(
                author=user,
                availability=availability,
                lessonNum=lessonNum,
                interval=interval,
                duration=duration,
                topic=topic,
                teacher=teacher
            )
        lessonRequest.save()

        return lessonRequest
        
    '''uname stands for username'''
    def _create_named_client_user(self, firstname, lastname, email, uname, password):
        studentnumber = find_next_available_student_number()
        created_student = Guardian.objects.create_user(
            first_name=firstname,
            last_name=lastname,
            email=email,
            username=uname,
            password=password,
        )
        GuardianProfile.objects.create(user=created_student, student_first_name=firstname, student_last_name=lastname, student_email=email)
        # GuardianProfile.objects.create(user=created_student, student_number=studentnumber)

    '''uname stands for username'''
    def _create_named_admin_user(self, firstname, lastname, email, uname, password):
        created_admin = Admin.objects.create_user(
            first_name=firstname,
            last_name=lastname,
            email=email,
            username=uname,
            password=password,
        )

    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email
    
    def _username(self, first_name, last_name):
        username = f'@{first_name}{last_name}'
        return username
