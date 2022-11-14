from django import forms
from .models import LessonRequest

class LessonRequestForm(forms.ModelForm):
    class Meta:
        model = LessonRequest
        fields = ['availability', 'lessonNum', 'interval', 'duration', 'topic', 'teacher']
        widgets = {
            'availability': forms.Textarea()
        }