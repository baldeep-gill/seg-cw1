from django.shortcuts import render, redirect
from .forms import LessonRequestForm, StudentSignUpForm, LogInForm, BookLessonRequestForm
from .models import LessonRequest, User, Lesson
from .forms import LessonRequestForm, StudentSignUpForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Admin, LessonRequest, Lesson, Student
from .helpers import only_admins, only_students
from django.core.exceptions import ObjectDoesNotExist

import datetime


# Create your views here.
def home(request):
    return render(request, 'home.html')

@login_required
@only_students
def lessons_success(request):
    current_student_id = request.user.id
    
    lessons = Lesson.objects.filter(student_id=current_student_id) #get(student=current_user) # we filter this by the username and then pass it 
    return render(request, 'successful_lessons_list.html', {'lessons': lessons})

@login_required
@only_students
def lesson_request(request):
    if request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
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



def book_lesson_request(request, request_id):
    try:
        lesson_request = LessonRequest.objects.get(id=request_id)
        student_making_request = User.objects.get(id=lesson_request.author_id)
    except ObjectDoesNotExist:
        return redirect("admin_requests")

    if request.method == 'POST':
        form = BookLessonRequestForm(request.POST)
        if form.is_valid():
            student = student_making_request
            duration = form.cleaned_data.get('duration')
            topic = form.cleaned_data.get('topic')
            teacher = form.cleaned_data.get('teacher')
            start_date = form.cleaned_data.get('start_date')
            time = form.cleaned_data.get('time')
            interval_between_lessons = form.cleaned_data.get('interval_between_lessons')
            number_of_lesons = form.cleaned_data.get('number_of_lessons')
            day = form.cleaned_data.get('day')

            new_date = datetime.datetime(start_date.year,start_date.month,start_date.day,time.hour,time.minute)
            weekday_dict = {"Monday":0,"Tuesday":1,"Wednesday":2,"Thursday":3,"Friday":4,"Saturday":5,"Sunday":6}
            while new_date.weekday() != weekday_dict[day]:
                tdelta = datetime.timedelta(days=1)
                new_date = new_date + tdelta

            tdelta = datetime.timedelta(weeks=interval_between_lessons)
            for i in range(number_of_lesons):
                lesson = Lesson.objects.create(
                    student=student,
                    date=new_date,
                    duration=duration,
                    topic=topic,
                    teacher=teacher
                )
                lesson.save()
                new_date = new_date + tdelta



            lesson_request.delete()
            return redirect('admin_requests')
    else:
        form = BookLessonRequestForm()
    return render(request, 'book_lesson_request.html', {'form': form, 'request_id':request_id, 'lesson_request':lesson_request,'student':student_making_request})

@login_required
@only_students
def student_home(request):
    return render(request, 'student_home.html')

@login_required
@only_admins
def admin_home(request):
    return render(request, 'admin_home.html')
    
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        next = request.POST.get('next') or ''
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if isinstance(user, Admin):
                    login(request, user)
                    redirect_url = next or 'admin_home'
                else:
                    login(request, user)
                    redirect_url = next or 'student_home'
                # in here we need to determine the type of the user to know which other redirect url we need to go to
                # TODO: determin the type of user
                #redirect user upon successful log i
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR, "User not found")
    else:
        next = request.GET.get('next') or ''
    form = LogInForm()
    return render(request, 'log_in.html', {'form':form})

def log_out(request):
    logout(request)
    return redirect('home')

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


def admin_requests(request):
    lesson_request_data = LessonRequest.objects.all()
    return render(request, 'admin_lesson_list.html', {'data': lesson_request_data})