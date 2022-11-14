from django.shortcuts import render
from .forms import LessonRequestForm

def home(request):
    return render(request, 'home.html')

def lesson_request(request):
    if request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            lessonReq = form.save()
    else:
        form = LessonRequestForm()
    return render(request, 'lesson_request.html', {'form': form})