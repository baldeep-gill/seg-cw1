"""Forms for the lessons app."""
from django import forms
from django.core.validators import RegexValidator
from .models import Student
from django.db.models import Max

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

    def find_id_for_new_student(self):
        id = 1
        while Student.objects.filter(student_number=id):
            id += 1
        return id

    def save(self):
        """Create a new user."""
        new_student_number = self.find_id_for_new_student()

        super().save(commit=False)
        student = Student.objects.create_user(
            #username = self.cleaned_data.get('username'),
            username = self.cleaned_data.get('first_name') + self.cleaned_data.get('last_name') + f'{new_student_number}' ,
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            #student_number = self.cleaned_data.get('student_number')
            student_number = new_student_number
        )
        return student



