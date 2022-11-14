from django import forms
from .models import LessonRequests

class LessonRequestForm(forms.ModelForm):
    class Meta:
        model = LessonRequests
        fields = ['availability', 'lessonNum', 'interval', 'duration', 'topic', 'teacher']
        widgets = {
            'availability': forms.Textarea()
        }