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

    # All users
    path('', views.home, name='home'),
    path('student_sign_up/', views.student_sign_up, name='student_sign_up'),
    path('log_in/', views.log_in, name='log_in'),
    path('password/', views.password, name='password'),
    path('profile/', views.profile, name='profile'),
    path('log_out/', views.log_out, name='log_out'),

    # Admin paths
    path('admin/home/', views.admin_home, name='admin_home'),
    path('admin/book_lesson_request/<int:request_id>', views.book_lesson_request, name='book_lesson_request'),
    path('admin/requests/', views.admin_requests, name='admin_requests'),
    path('admin/lessons/', views.admin_lessons, name='admin_lessons'),
    path('admin/lessons/edit/<lesson_id>', views.edit_lessons, name='edit_lessons'),
    path('admin/payments', views.all_student_balances, name='payments'),
    path('admin/payments/<int:student_id>', views.student_balance, name='student_payments'),
    path('admin/payments/<int:student_id>/<int:invoice_id>', views.approve_transaction, name='approve_transaction'),
    path('admin/lessons/delete/<lesson_id>', views.delete_lessons, name='delete_lessons'),
    path('admin/terms', views.admin_terms, name='admin_terms'),
    path('admin/terms/delete/<term_id>', views.delete_terms, name='delete_terms'),
    path('admin/terms/edit/<term_id>', views.edit_terms, name='edit_terms'),

    # Student paths
    path('student/lesson_request/', views.lesson_request, name='lesson_request'),
    path('student/home/', views.student_home, name='student_home'),
    path('student/requests/', views.show_requests, name='show_requests'),
    path('student/invoices/', views.show_invoices, name='show_invoices'),
    path('student/invoices/<invoice_id>', views.show_invoice_lessons, name='show_invoice_lessons'),
    path('student/requests/edit/<lesson_id>', views.edit_requests, name='edit_requests'),
    path('student/requests/delete/<lesson_id>', views.delete_requests, name='delete_requests'),
    path('student/lessons/list', views.lessons_success, name='lesson_list'),
    path('student/balance/', views.balance, name='balance'),

    # Guardian paths
    path('guardian_sign_up/', views.guardian_sign_up, name='guardian_sign_up'),
    path('guardian/home/', views.guardian_home, name='guardian_home'),
    path('guardian/add/', views.add_student, name='add_student'),
    path('guardian/book/', views.book_for_student, name='book_for_student'),
]
