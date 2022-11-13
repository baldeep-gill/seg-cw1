from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'base.html')

def student_sign_up(request):
    return render(request,'student_sign_up.html')
