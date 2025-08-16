from django.urls import path
from . import views as user_views
from .views import CustomLogoutView
from . import views 

# This namespace lets you use {% url 'users:...' %} in templates
app_name = "users"

urlpatterns = [
    path('', user_views.home, name='user-home'),
    path('register/', user_views.register, name='register'),
    path('dashboard/', user_views.dashboard, name='dashboard'),
    path('student-dashboard/', user_views.student_dashboard, name='student_dashboard'),
   path('faculty-dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]
