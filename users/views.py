from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.views import View  # ✅ Import View
from django.contrib.auth import logout  # ✅ Import logout

from .forms import UserRegisterForm
from courses.models import Course, Lesson, Enrollment  # Import Course & Lesson models


# ---------- Role Check Helpers ----------
def is_student(user):
    return getattr(user, 'role', None) == 'student'

def is_faculty(user):
    return getattr(user, 'role', None) == 'faculty'


# ---------- Home ----------
def home(request):
    return HttpResponse("Users App Home Page")


# ---------- Registration ----------
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Registration successful! Please log in.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


# ---------- Dashboard Redirect ----------
@login_required
def dashboard(request):
    if request.user.role == 'student':
        return redirect('users:student_dashboard')
    elif request.user.role == 'faculty':
        return redirect('users:faculty_dashboard')
    return HttpResponse("Invalid user role")


# ---------- Student Dashboard ----------
@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    enrolled_courses = Course.objects.filter(enrollments__student=request.user)
    available_courses = Course.objects.exclude(enrollments__student=request.user)

    return render(request, 'users/student_dashboard.html', {
        'enrolled_courses': enrolled_courses,
        'available_courses': available_courses,
    })


# ---------- Faculty Dashboard ----------
@login_required
@user_passes_test(is_faculty)
def faculty_dashboard(request):
    my_courses = (
        Course.objects
        .filter(created_by=request.user)
        .prefetch_related('lesson_set')
    )
    for course in my_courses:
        course.lessons = course.lesson_set.all().order_by('id')
    return render(request, 'users/faculty_dashboard.html', {'my_courses': my_courses})


class CustomLogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, "✅ You have successfully logged out.")
        return redirect('login')