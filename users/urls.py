from django.urls import path
from . import views
from .views import CustomLogoutView

# This namespace lets you use {% url 'users:...' %} in templates
app_name = "users"

urlpatterns = [
    path('', views.home, name='user-home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student-dashboard'),
    path('faculty-dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]
