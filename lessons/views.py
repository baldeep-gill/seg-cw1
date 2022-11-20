from django.shortcuts import render, redirect
from .forms import LessonRequestForm, StudentSignUpForm, LogInForm
from .models import LessonRequest, User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.
def home(request):
    return render(request, 'home.html')

def lesson_request(request):
    if request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            # No need for 'if user.is_authenticated' as this is handled on the home.html template
            current_user = request.user
            availability = form.cleaned_data.get('availability')
            lessonNum = form.cleaned_data.get('lessonNum')
            interval = form.cleaned_data.get('interval')
            duration = form.cleaned_data.get('duration')
            topic = form.cleaned_data.get('topic')
            teacher = form.cleaned_data.get('teacher')
            lessonRequest = LessonRequest.objects.create(
                author=current_user,
                availability=availability,
                lessonNum=lessonNum,
                interval=interval,
                duration=duration,
                topic=topic,
                teacher=teacher
            )
            lessonRequest.save()
            return redirect('lesson_request')
    else:
        form = LessonRequestForm()
    return render(request, 'lesson_request.html', {'form': form})

def student_home(request):
    return render(request, 'student_home.html')

def admin_home(request):
    return render(request, 'admin_home.html')

def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                #redirect user upon successful log in
                return redirect('lesson_request')
        messages.add_message(request, messages.ERROR, "User not found")
    form = LogInForm()
    return render(request, 'log_in.html', {'form':form})

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

