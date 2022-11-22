"""msms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from lessons import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('lesson-request/', views.lesson_request, name = 'lesson_request'),
    path('student_sign_up/', views.student_sign_up, name='student_sign_up'),
    path('student/home', views.student_home, name='student_home'),
    #TODO admin/home leads to django admin interface so cant use it, have used msmadmin for now but there is probably a better name for it
    path('msmadmin/home', views.admin_home, name='admin_home'),
    path('msmadmin/requests', views.admin_requests, name='admin_requests'),

]
