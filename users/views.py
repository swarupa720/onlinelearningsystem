from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.urls import reverse_lazy

from .forms import UserRegisterForm

# Home view (optional)
def home(request):
    return HttpResponse("Users App Home Page")

# Register view
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirects to login after successful registration
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# Dashboard view to redirect based on user role
@login_required
def dashboard(request):
    if request.user.role == 'student':
        return redirect('student_dashboard')
    elif request.user.role == 'faculty':
        return redirect('faculty_dashboard')
    else:
        return HttpResponse("Invalid user role")

# Student dashboard
@login_required
def student_dashboard(request):
    return render(request, 'users/student_dashboard.html')

# Faculty dashboard
@login_required
def faculty_dashboard(request):
    return render(request, 'users/faculty_dashboard.html')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')  # redirect after logout

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "✅ You have been successfully logged out.")
        return super().dispatch(request, *args, **kwargs)