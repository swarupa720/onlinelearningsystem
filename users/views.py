from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views import View
from django.contrib.auth import logout

from .forms import UserRegisterForm
from courses.models import Course, Enrollment


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
            user = form.save(commit=False)
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()
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
    # Already enrolled courses
    enrolled_courses = Course.objects.filter(enrollments__student=request.user)

    # Courses student has NOT enrolled in yet
    enrolled_ids = enrolled_courses.values_list('id', flat=True)
    available_courses = Course.objects.exclude(id__in=enrolled_ids)

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
        .prefetch_related('lessons')  # Use related_name='lessons' from Lesson model
    )
    return render(request, 'users/faculty_dashboard.html', {'my_courses': my_courses})


# ---------- Logout ----------
class CustomLogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, "✅ You have successfully logged out.")
        return redirect('login')
