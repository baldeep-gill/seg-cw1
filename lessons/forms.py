from django import forms
from django.core.validators import RegexValidator, MinValueValidator
from .models import User, Student, StudentProfile, LessonRequest, Lesson, Term
from django.db.models import Max
from .helpers import find_next_available_student_number, day_of_the_week_validator,\
    does_date_fall_in_an_existing_term, is_a_term_validator,does_date_fall_in_given_term,\
    get_next_term, are_all_terms_outdated, are_there_any_terms, check_lessons_fit_in_given_dates,\
    calculate_how_many_lessons_fit_in_given_dates
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateTimeField
from django.core.exceptions import ValidationError

class LessonRequestForm(forms.ModelForm):
    """Form for requesting a lesson"""
    class Meta:
        model = LessonRequest
        fields = ['availability', 'lessonNum', 'interval', 'duration', 'topic', 'teacher']
        """widgets = {
            'availability': forms.DateTimeInput()
        }"""



class BookLessonRequestForm(forms.ModelForm):
    """Form for fulfilling/booking lesson requests"""
    class Meta:
        model = Lesson
        fields = ['duration','topic','teacher']

    term = forms.CharField(label="Term",validators=[is_a_term_validator])
    start_date = forms.DateTimeField(label="Start Date",widget=forms.SelectDateWidget)
    end_date = forms.DateTimeField(label="End Date",widget=forms.SelectDateWidget)
    day = forms.CharField(label="Day of the week",validators=[day_of_the_week_validator])
    time = forms.TimeField(label="Time")
    interval_between_lessons = forms.IntegerField(label="Weeks Between lessons",validators=[MinValueValidator(1)])
    number_of_lessons = forms.IntegerField(label="Number of lessons",validators=[MinValueValidator(1)])

    def __init__(self,lesson_request_id=None,*args,**kwargs):
        super(BookLessonRequestForm, self).__init__(*args,**kwargs)
        next_term = get_next_term()
        if next_term:
            self.fields['term'].initial = next_term.name
            self.fields['start_date'].initial = next_term.start_date
            self.fields['end_date'].initial = next_term.end_date
        else:
            self.fields['term'].initial = "No Upcoming terms found, you need to create one first!"

        # Auto fill in rest of fields from lesson request
        if lesson_request_id:
            lesson_request = LessonRequest.objects.get(id=lesson_request_id)
            self.fields['duration'].initial = lesson_request.duration
            self.fields['topic'].initial = lesson_request.topic
            self.fields['teacher'].initial = lesson_request.teacher
            self.fields['interval_between_lessons'].initial = lesson_request.interval
            self.fields['number_of_lessons'].initial = lesson_request.lessonNum

    def clean(self):
        super().clean()
        if Term.objects.count() == 0:
            self.add_error('term','You have currently created no terms. You will need to create a term before booking a lesson')

        if are_all_terms_outdated():
            self.add_error('term','All your terms are outdated, add some new ones')

        start_date = self.cleaned_data.get('start_date')
        term_chosen = Term.objects.filter(name=self.cleaned_data.get('term')).first()
        if start_date and term_chosen:
            if not does_date_fall_in_given_term(start_date,term_chosen):
                self.add_error('start_date', f'This date does not fall in the term given! '
                                             f'Term given starts on {term_chosen.start_date.date().__str__()} and ends on {term_chosen.end_date.date().__str__()}'
                               )

        end_date = self.cleaned_data.get('end_date')
        if end_date and term_chosen:
            if not does_date_fall_in_given_term(end_date,term_chosen):
                self.add_error('end_date', f'This date does not fall in the term given! '
                                             f'Term given starts on {term_chosen.start_date.date().__str__()} and ends on {term_chosen.end_date.date().__str__()}'
                               )

        if end_date and start_date:
            if end_date <= start_date:
                self.add_error('end_date', f'End date must be after the start date!')

        # Checking that the lessons specified in form can fit in between dates given
        day = self.cleaned_data.get('day')
        number_of_lessons = self.cleaned_data.get('number_of_lessons')
        interval = self.cleaned_data.get('interval_between_lessons')
        if start_date and end_date and day and number_of_lessons and interval:
            if not check_lessons_fit_in_given_dates(start_date,end_date,number_of_lessons,interval,day):
                self.add_error('number_of_lessons', f'You cannot fit this number of lessons with the given interval in between the start and end dates!'
                               f' Maximum number of lessons with this interval and dates is {calculate_how_many_lessons_fit_in_given_dates(start_date,end_date,number_of_lessons,interval,day)}')

class EditForm(forms.ModelForm):
    """Form to update lesson request"""
    class Meta:
        model = LessonRequest
        fields = ['availability', 'lessonNum', 'interval', 'duration', 'topic', 'teacher']

class EditLessonForm(forms.ModelForm):
    """Form to update lesson"""
    class Meta:
        model = Lesson
        fields = ['date', 'duration', 'topic', 'teacher']

"""Forms for the lessons app."""
class LogInForm(forms.Form):
    username = forms.CharField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

class StudentSignUpForm(forms.ModelForm):
    """Form enabling unregistered students to sign up."""

    class Meta:
        """Form options."""

        model = Student
        fields = ['first_name', 'last_name', 'email']
        widgets = { 'bio': forms.Textarea() }

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        """Create a new user."""
        new_student_number = find_next_available_student_number()

        super().save(commit=False)
        student = Student.objects.create_user(
            username = self.cleaned_data.get('first_name') + self.cleaned_data.get('last_name') + f'{new_student_number}' ,
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )

        StudentProfile.objects.create(user=student, student_number = new_student_number)
        return student

class PasswordForm(forms.Form):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())
    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class TermForm(forms.ModelForm):
    """Form for creating new school terms"""
    class Meta:
        model = Term
        fields = ['name','start_date','end_date']
        widgets = {'start_date':forms.SelectDateWidget,'end_date':forms.SelectDateWidget}

    def clean(self):
        super().clean()
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        if end_date < start_date:
            self.add_error('end_date','End date must be after start date')

        if does_date_fall_in_an_existing_term(start_date):
            self.add_error('start_date','This date falls within an existing term!')

        if does_date_fall_in_an_existing_term(end_date):
            self.add_error('end_date','This date falls within an existing term!')


