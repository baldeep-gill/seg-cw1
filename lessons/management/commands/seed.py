from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from faker import Faker
from lessons.models import Student
from lessons.management.commands.unseed import Command as Unseeder
from lessons.helpers import find_next_available_student_number

class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_COUNT = 100

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        user_count = 0
        Unseeder.handle(self)
        self._create_named_student_user(firstname="John", lastname="Doe", email="john.doe@example.org", password="Password123")
        
        while user_count < Command.USER_COUNT:
            print(f'Seeding user {user_count}',  end='\r')
            try:
                self._create_user()
            except (IntegrityError):
                continue
            user_count += 1
        print('User seeding complete')

    def _create_user(self):
        student_number = find_next_available_student_number()
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name, last_name)
        Student.objects.create_user(
            student_number,
            student_number=student_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=Command.PASSWORD,
        )
    
    def _create_named_student_user(self, firstname, lastname, email, password):
        student_number = find_next_available_student_number()

        Student.objects.create_user(
            student_number,
            student_number=student_number,
            first_name=firstname,
            last_name=lastname,
            email=email,
            password=password,
        )

    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email
