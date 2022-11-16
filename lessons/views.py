
from django.shortcuts import render, redirect
from .forms import StudentSignUpForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Create your views here.

def home(request):
    return render(request, 'home.html')

def student_sign_up(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # login user after they have signed up
            # login(request, user)
            return redirect('home')
    else:
        # creating empty sign up form
        form = StudentSignUpForm()
    return render(request, 'student_sign_up.html',{'form': form})



