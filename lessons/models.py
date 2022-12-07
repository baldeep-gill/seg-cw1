"""Models in the lessons app."""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from libgravatar import Gravatar
from django.core.validators import MinValueValidator, MaxValueValidator
import pytz
from django.utils import timezone

'''The base user that all users inherit'''
class User(AbstractUser):
    '''We will only have two types either a user or an admin (could be extended later on)'''
    class Types(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        STUDENT = "STUDENT", 'Student'
        GUARDIAN = "GUARDIAN", 'Guardian'
    
    '''defualt role'''
    base_role = Types.ADMIN

    '''Fields that are shared by all users'''
    type = models.CharField(gettext_lazy("Type"), max_length=50, choices=Types.choices, default=base_role)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)

    def full_name(self):
        """Return the full name of the student"""
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.type = self.base_role
        return super().save(*args, **kwargs)


'''Student users'''
# manages all students 
class StudentManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.STUDENT)

# A new table to store the student number and extra information about the user later on
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_number = models.IntegerField(unique=True,blank=False)

# Student user
class Student(User):
    base_role = User.Types.STUDENT
    students = StudentManager()
    
    @property
    def more(self):
        '''this refers to the table in the database'''
        return self.studentprofile

    @property
    def invoices(self):
        return Invoice.objects.filter(student=self)
    
    @property
    def transfers(self):
        # Make sure incomplete transfers aren't repeated when displayed separately

        return Transfer.objects.filter(invoice__student=self)

    @property
    def grouped_transfers(self):
        # Make sure incomplete transfers aren't repeated when displayed separately
        transfers_per_invoice = {}
        for transfer in Transfer.objects.filter(invoice__student=self):
            if(transfers_per_invoice.get(transfer.invoice)):
                transfers_per_invoice[transfer.invoice].append(transfer)
            else:
                transfers_per_invoice[transfer.invoice] = [transfer]
        
        return transfers_per_invoice

    @property
    def unpaid_invoices(self):
        transfer_list = self.transfers
        invoice_list = self.invoices.exclude(id__in=transfer_list.values('invoice_id'))
        return invoice_list

    @property
    def underpaid_invoices(self):
        transfer_list = self.transfers
        # invoice_list = self.invoices.filter(id__in=transfer_list.values('invoice_id'))
        underpaid_invoices = {}
        for transfer in transfer_list:
            if transfer.amount_received < transfer.invoice.price:
                if(underpaid_invoices.get(transfer.invoice)):
                    underpaid_invoices[transfer.invoice] += transfer.amount_received
                    if(underpaid_invoices[transfer.invoice] >= transfer.invoice.price):
                        # Removes invoice from the list of underpaid invoices if the invoice is paid fully or overpaid
                        del underpaid_invoices[transfer.invoice]
                else:
                    underpaid_invoices[transfer.invoice] = transfer.amount_received
        
        

        return underpaid_invoices

    class Meta:
        proxy = True

'''Guardian users'''
# manages all guardians 
class GuardianManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.GUARDIAN)

# A new table to store the student number and extra information about the user later on
class GuardianProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    student_first_name = models.CharField(max_length=50, blank=False)
    student_last_name = models.CharField(max_length=50, blank=False)
    student_email = models.EmailField(unique=True, blank=False)

# Guardian user
class Guardian(User):
    base_role = User.Types.GUARDIAN
    guardians = GuardianManager()

    class Meta:
        proxy = True

'''Admin users'''
# manages all Admins 
class AdminManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type=User.Types.ADMIN)

# Admin user
class Admin(User):
    base_role = User.Types.ADMIN
    admins = AdminManager()
    
    class Meta:
        proxy = True


class LessonRequest(models.Model):
    """Code to model a students request for a lesson"""

    author = models.ForeignKey(
        Student,
        on_delete = models.CASCADE,
        blank = False,
    )

    # Ask which days of the week the student is available for lessons #
    # TODO: figure out how to get bootstrap to create a datetime field input 
    """availability = models.DateTimeField(
        auto_now = False,
        auto_now_add = False,
    )"""

    availability = models.CharField(
        blank = False,
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




class Invoice(models.Model):
    """Models an invoice for a set of lessons"""

    # Invoice who student is for
    student = models.ForeignKey(
        Student,
        on_delete = models.CASCADE,
        blank = False,
    )

    # Date and time when invoice was generated
    date = models.DateTimeField(
        blank=False
    )

    # Number of the invoice for the student
    invoice_number = models.IntegerField(
        blank = False,
    )

    # Unique reference number which can be used to identify individual invoices
    # Is of the form student_number-invoice number
    @property
    def unique_reference_number(self):
        return f'{self.student.id}-{self.invoice_number}'

    @property
    def lessons(self):
        """Returns all the lessons belonging to this invoice"""
        return Lesson.objects.filter(invoice=self)

    @property
    def price(self):
        """Returns the total price associated with this invoice
        Sum of the prices of the lessons"""
        price = 0
        for lesson in self.lessons:
            price += lesson.price
        return price
        
    @property
    def paid(self):
        transfer = self.associated_transfers
        if transfer:
            return self.amount_paid >= self.price
        else:
            return False
    
    @property
    def at_least_partially_paid(self):
        transfer = self.associated_transfers
        if transfer:
            return True
        else:
            return False

    @property
    def associated_transfers(self):
        return Transfer.objects.filter(invoice=self)

    @property
    def amount_paid(self):
        amount = 0
        for transfer in Transfer.objects.filter(invoice=self):
            amount += transfer.amount_received
        
        return amount


def present_or_past_date(value):
    if value > timezone.now():
        raise ValidationError("The date cannot be in the future!")
    return value

class Transfer(models.Model):
    """Models a transfer completed by a student"""
    
    # The date and time when the transfer was received 
    date_received = models.DateTimeField(blank=False, default=timezone.now, validators=[present_or_past_date])

    transfer_id = models.IntegerField(blank=False, unique=True)

    amount_received = models.IntegerField(blank=False)

    
    """Administrator who verified the payment.
    ALl payments are done through the school bank account
    and have to be checked by an administrator user"""
    verifier = models.ForeignKey(
        Admin,
        on_delete = models.CASCADE,
        blank = False,
    )

    invoice = models.ForeignKey(
        Invoice, 
        on_delete = models.CASCADE,
        blank = False
    )
    
    @property
    def lessons(self):
        return Lesson.objects.filter(invoice=self.invoice())


class Lesson(models.Model):
    """Models a booked lesson for a student"""

    # Lesson who the student is for, Lesson can't exist without an associated student
    student = models.ForeignKey(
        Student,
        on_delete = models.CASCADE,
        blank = False,
    )

    # Invoice lesson is part of, Lesson can't exist without an associated invoice
    invoice = models.ForeignKey(
        Invoice,
        on_delete = models.CASCADE,
        blank = False,
    )

    # Date and time of lesson
    date = models.DateTimeField(
        blank=False,
    )

    # Duration of each lesson in minutes
    duration = models.IntegerField(
        blank = False,
        default = 60,
        validators = [
            # We'll say a lesson should be a minimum of 30 mins, maximum of 2 hours #
            MinValueValidator(30),
            MaxValueValidator(120),
        ],
    )

    # What the lesson is about
    topic = models.CharField(
        max_length = 50,
        blank=False
    )

    # Who teaches the lesson
    teacher = models.CharField(
        blank = False,
        max_length = 50,
    )

    @property
    def price(self):
        """Calculates the price of this individual lesson"""
        return self.price_per_minute * self.duration

    @property
    def price_per_minute(self):
        """Returns the cost of this lesson per minute in pounds/£"""
        return 1


class Term(models.Model):
    """Models a school term"""

    # Name of term, ie 'term 1' or 'Summer term'
    name = models.CharField(
        max_length = 50,
        unique = True,
        blank=False
    )

    # Start date of term
    start_date = models.DateTimeField(
        blank=False,
    )

    # End date of term
    end_date = models.DateTimeField(
        blank=False,
    )










