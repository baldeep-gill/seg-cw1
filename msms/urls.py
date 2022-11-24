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
    path('django/admin/', admin.site.urls),

    path('', views.home, name='home'),
    path('student_sign_up/', views.student_sign_up, name='student_sign_up'),
    path('log_in/', views.log_in, name='log_in'),

    path('student/home/', views.student_home, name='student_home'),
    path('student/lesson_request/', views.lesson_request, name='lesson_request'),
    path('student/log_out/', views.log_out, name='log_out'),

    path('admin/home/', views.admin_home, name='admin_home'),
    path('admin/unfulfilled_requests/', views.admin_requests, name='admin_requests'),
    path('admin/book_lesson_request/<int:request_id>', views.book_lesson_request, name='book_lesson_request'),

    # for branch 06
    path('student/lessons/list', views.lessons_success, name='lesson_list'),

]
