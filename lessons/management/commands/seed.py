from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from faker import Faker
from lessons.models import Student, StudentProfile, Admin
from lessons.helpers import find_next_available_student_number

class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_COUNT = 101
    # Includes 100 students, 1 additional admin

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.seedusers()
    
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

    def _create_user(self, isAdmin=False):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        student_email = self._email(first_name, last_name)
        username = self._username(first_name, last_name)
        admin_email = self._email(first_name, last_name)
        if(isAdmin): self._create_named_admin_user(first_name, last_name, admin_email, username, Command.PASSWORD)
        else: self._create_named_student_user(first_name, last_name, student_email, username, Command.PASSWORD)
       
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
