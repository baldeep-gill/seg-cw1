from django.shortcuts import render, redirect
from .forms import LessonRequestForm, StudentSignUpForm, LogInForm
from .models import LessonRequest, User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Admin, Student, User

# Create your views here.
def home(request):
    return render(request, 'home.html')

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

@login_required
def student_home(request):
    try:
        if(Student.students.get(username=request.user.get_username())):
            return render(request, 'student_home.html')
    except User.DoesNotExist:
        return render(request, 'admin_home.html')

@login_required
def admin_home(request):
    try:
        if(Admin.admins.get(username=request.user.get_username()).exists()):
            return render(request, 'admin_home.html')
    except User.DoesNotExist:
        return render(request, 'student_home.html')
    
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        next = request.POST.get('next') or ''
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
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
        messages.add_message(request, messages.ERROR, "User not found, please try again.")
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

