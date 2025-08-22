from django.contrib import admin
from django.urls import path, include
from users.views import CustomLogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Users app routes
    path('users/', include(('users.urls', 'users'), namespace='users')),

    # Courses app routes
    path('courses/', include('courses.urls')),

    # Authentication routes
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # Root URL → Login page
    path('', auth_views.LoginView.as_view(template_name='users/login.html'), name='home'),
]
