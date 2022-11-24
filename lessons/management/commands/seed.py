from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from faker import Faker
from lessons.models import Student, StudentProfile, Admin
from lessons.helpers import find_next_available_student_number

class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_COUNT = 100

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        user_count = 0        
        while user_count < Command.USER_COUNT:
            print(f'Seeding user {user_count}',  end='\r')
            try:
                self._create_user()
            except (IntegrityError):
                continue
            user_count += 1
        print('User seeding complete')

    def _create_user(self):
        random_number = self.faker.random.randint(0, 100000)
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        student_email = self._email(first_name, last_name)
        student_username = self._username(first_name, last_name)
        admin_username = self._username((first_name + str(random_number)), last_name)
        admin_email = self._email(admin_username, last_name)
        self._create_named_student_user(first_name, last_name, student_email, student_username, Command.PASSWORD)
        self._create_named_admin_user(first_name, last_name, admin_email, admin_username, Command.PASSWORD)
       
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
        Admin.objects.create_user(
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
