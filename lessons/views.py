
from django.shortcuts import render, redirect
from .forms import StudentSignUpForm, LogInForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Admin, Student, User

# Create your views here.

def home(request):
    return render(request, 'home.html')

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
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                redirect_url = next or 'student_home'
                # in here we need to determine the type of the user to know which other redirect url we need to go to
                # TODO: determin the type of user
                #redirect user upon successful log in
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



