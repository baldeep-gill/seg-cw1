from django.shortcuts import render
from .forms import LessonRequestForm

# Create your views here.

def home(request):
    return render(request, 'base.html')

def lesson_request(request):
    if request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            lessonReq = form.save()
    else:
        form = LessonRequestForm()
    return render(request, 'lesson_request.html', {'form': form})

