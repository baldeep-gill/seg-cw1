import pytz
from django.shortcuts import render, redirect
from .forms import LessonRequestForm, StudentSignUpForm, LogInForm, BookLessonRequestForm, EditForm, PasswordForm, UserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from .models import Admin, LessonRequest, Lesson, Student, User, Invoice, Transfer
from .helpers import only_admins, only_students, get_next_given_day_of_week_after_date_given, find_next_available_invoice_number_for_student, login_prohibited, find_next_available_transfer_id
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone


import datetime

# Create your views here.
@login_prohibited
def home(request):
    return render(request, 'home.html')

@login_required
@only_students
def balance(request):
    # first we need to get the student
    current_student_id = request.user.id

    student = Student.objects.get(id=current_student_id)

    # then we retrieve all the lessons they have from the db
    # invoices = Invoice.objects.filter(student_id=current_student_id)
    invoices = student.unpaid_invoices
    transfers = student.transfers
    
    # total money owed
    total_due = 0
    for invoice in invoices:
        total_due += invoice.price

    total_paid = 0
    for transfer in transfers:
        total_paid += transfer.invoice.price


    return render(request, 'balance.html', {'invoices': invoices, 'transfers': transfers, 'total_paid':total_paid, 'total_due': total_due})

@login_required
@only_students
def lessons_success(request):
    current_student_id = request.user.id
    lessons = Lesson.objects.filter(student_id=current_student_id)
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
            return redirect('student_home')
    else:
        form = LessonRequestForm()
    return render(request, 'lesson_request.html', {'form': form})


@login_required
@only_admins
def book_lesson_request(request, request_id):
    """View to allow admins to fulfill/book a lesson request"""
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
            number_of_lessons = form.cleaned_data.get('number_of_lessons')
            day = form.cleaned_data.get('day')

            #combines the start date picked and the time each day into one dateTime object
            new_date = datetime.datetime(start_date.year,start_date.month,start_date.day,time.hour,time.minute,tzinfo=pytz.UTC)
            new_date = get_next_given_day_of_week_after_date_given(new_date,day)

            #generate an invoice for the lessons we will generate
            new_invoice_number = find_next_available_invoice_number_for_student(student)
            invoice = Invoice.objects.create(
                student=student,
                date=datetime.datetime.now(tz=pytz.UTC),
                invoice_number=new_invoice_number,
            )
            invoice.save()

            #we will generate a lesson every lesson interval weeks at the time given
            tdelta = datetime.timedelta(weeks=interval_between_lessons)
            for i in range(number_of_lessons):
                lesson = Lesson.objects.create(
                    student=student,
                    invoice=invoice,
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
    return render(request, 'book_lesson_request.html', {'form': form,'lesson_request':lesson_request,'student':student_making_request})

@login_required
@only_students
def student_home(request):
    return render(request, 'student_home.html')

@login_required
@only_admins
def admin_home(request):
    return render(request, 'admin_home.html')

@login_prohibited
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
    return render(request, 'log_in.html', {'form':form, 'next': next})

def log_out(request):
    logout(request)
    return redirect('home')

@login_prohibited
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

@login_required
@only_admins
def admin_requests(request):
    lesson_request_data = LessonRequest.objects.all()
    return render(request, 'admin_lesson_list.html', {'data': lesson_request_data})

@login_required
@only_students
def show_requests(request):
    user = request.user
    lesson_requests = LessonRequest.objects.filter(author=user)
    return render(request, 'show_requests.html', {'user': user, 'lesson_requests': lesson_requests})

'''allow users to change passwords'''
@login_required
def password(request):
    current_user = request.user
    if request.method == 'POST':
        form = PasswordForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if check_password(password, current_user.password):
                new_password = form.cleaned_data.get('new_password')
                current_user.set_password(new_password)
                current_user.save()
                login(request, current_user)
                messages.add_message(request, messages.SUCCESS, "Password updated!")
                if isinstance(current_user, Admin):
                    return redirect('admin_home')
                else:
                    return redirect('student_home')

    form = PasswordForm()
    return render(request, 'password.html', {'form': form})

@login_required
def profile(request):
    current_user = request.user
    if request.method == 'POST':
        form = UserForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            if isinstance(current_user, Admin):
                return redirect('admin_home')
            else:
                return redirect('student_home')
    else:
        form = UserForm(instance=current_user)
    return render(request, 'profile.html', {'form': form})

@login_required
@only_students
def edit_requests(request, lesson_id):
    try:
        current_lesson = LessonRequest.objects.get(id=lesson_id)
    except ObjectDoesNotExist:
        return redirect('show_requests')
    else:
        if request.method == 'POST':
            form = EditForm(instance=current_lesson, data=request.POST)
            if form.is_valid():
                form.save()
                return redirect('show_requests')
        else:
            form = EditForm(instance=current_lesson)
        return render(request, 'edit_requests.html', {'form': form, 'lesson_id': lesson_id})

@login_required
@only_students
def delete_requests(request, lesson_id):
    try:
        current_lesson = LessonRequest.objects.get(id=lesson_id)
    except ObjectDoesNotExist:
        return redirect('show_requests')
    else:
        user = request.user
        if current_lesson.author != user:
            return redirect('student_home')
        else:
            current_lesson.delete()
            return redirect('show_requests')

@login_required
@only_students
def show_invoices(request):
    current_student = request.user
    invoices = Invoice.objects.filter(student=current_student)
    return render(request, 'invoices_list.html', {'invoices': invoices})

@login_required
@only_admins
def all_student_balances(request):
    all_students = Student.objects.all()
    balances = {}
    for student in all_students:
        student_invoices = Invoice.objects.filter(student=student)
        balance = 0
        for invoice in student_invoices:
            if(Transfer.objects.filter(invoice=invoice).count() == 0):
                balance += invoice.price
      
        balances[student] = balance

    return render(request, 'admin_payments.html', {'balances': balances})

@login_required
@only_admins
def student_balance(request, student_id):
    student = Student.objects.filter(id=student_id).first()
    
    transfer_list = student.transfers
    invoice_list = student.unpaid_invoices
    # student.invoices.exclude(id__in=transfer_list.values('invoice_id'))
    
    return render(request, 'admin_student_payments.html', {'invoices': invoice_list, 'transfers': transfer_list, 'student': student})

@login_required
@only_admins
def approve_transaction(request, student_id, invoice_id):
    if request.method == 'POST':
        current_admin = request.user
        invoice = Invoice.objects.filter(student_id=student_id).filter(invoice_number=invoice_id)
        next_transfer_id = find_next_available_transfer_id()
        transfer = Transfer.objects.create(date_received=timezone.now(), transfer_id=next_transfer_id, verifier=current_admin, invoice=invoice.first())
        transfer.save()

    return redirect('student_payments', student_id=student_id)

@login_required
@only_students
def show_invoice_lessons(request, invoice_id):
    """Shows the lessons associated with a given invoice"""
    try:
        current_invoice = Invoice.objects.get(id=invoice_id)
    except ObjectDoesNotExist:
        return redirect('show_invoices')
    else:
        lessons_to_display = current_invoice.lessons
        return render(request, 'show_invoice_lessons.html', {'lessons': lessons_to_display, 'invoice':current_invoice})

