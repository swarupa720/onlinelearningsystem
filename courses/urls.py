from django.urls import path
from . import views  # Import views from this app

urlpatterns = [
    # Temporary home page
    path('', views.home, name='courses-home'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson-detail'),
    path('lesson/<int:lesson_id>/quiz/', views.quiz_view, name='quiz_view'),
    path('lesson/<int:lesson_id>/quiz/submit/', views.quiz_submit, name='quiz_submit'),
]
