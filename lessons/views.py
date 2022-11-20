from django.shortcuts import render, redirect
from .forms import LessonRequestForm, StudentSignUpForm

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
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

def student_home(request):
    return render(request, 'student_home.html')

def admin_home(request):
    return render(request, 'admin_home.html')

def student_sign_up(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            #redirected to home after sign up so they can login
            return render(request, 'student_sign_up_confirmation.html')

    else:
        # creating empty sign up form
        form = StudentSignUpForm()
    return render(request, 'student_sign_up.html',{'form': form})

