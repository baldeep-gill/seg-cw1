from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from faker import Faker
from lessons.models import Student, StudentProfile, Admin, LessonRequest
from lessons.helpers import find_next_available_student_number
from datetime import datetime, timedelta
from django.core.management import call_command

class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_COUNT = 101
    # Includes 100 students, 1 additional admin
    LESSON_COUNT = 15
    # TODO: Use the LESSON_COUNT and USER_COUNT in tests rather than manually written numbers
    
    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        call_command('unseed')
        self.seedusers()
        self.seedlessonrequests()
    
    def seedusers(self):
        self._create_named_student_user(firstname="John", lastname="Doe", email="john.doe@example.com", password="Password123", uname=self._username("John", "Doe"))
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
        print('Seeded ' + str(Student.objects.count()) + ' students')
        print('Seeded ' + str(Admin.objects.count()) + ' admins')

        
    def seedlessonrequests(self):
        lesson_count = 0        
        while lesson_count < Command.LESSON_COUNT:
            print(f'Seeding user {lesson_count}',  end='\r')
            try:
                # seeds 1 admin after 100 students
                self._create_lesson()
            except (IntegrityError):
                continue
            lesson_count += 1
        print('lesson request seeding complete')
        print('Seeded ' + str(LessonRequest.objects.count()) + ' requests')

    def _create_user(self, isAdmin=False):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name, last_name)
        username = self._username(first_name, last_name)
        if(isAdmin): self._create_named_admin_user(first_name, last_name, email, username, Command.PASSWORD)
        else: self._create_named_student_user(first_name, last_name, email, username, Command.PASSWORD)
       
    def _create_lesson(self):
        """Selects a random student user from the database"""
        user = Student.objects.order_by('?').first()
        lessonNum = self.faker.random.randint(1, 5)
        interval = self.faker.random.randint(1, lessonNum)
        duration = round(self.faker.random.randint(30, 180))


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
        
    '''uname stands for username'''
    def _create_named_student_user(self, firstname, lastname, email, uname, password):
        studentnumber = find_next_available_student_number()
        created_student = Student.objects.create_user(
            first_name=firstname,
            last_name=lastname,
            email=email,
            username=uname,
            password=password,
        )
        StudentProfile.objects.create(user=created_student, student_number=studentnumber)

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
