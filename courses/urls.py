from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course-list'), 
    path('course/<int:course_id>/', views.course_detail, name='course-detail'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson-detail'),
    path('lesson/<int:lesson_id>/quiz/', views.quiz_view, name='quiz'),
    path('lesson/<int:lesson_id>/quiz/submit/', views.quiz_submit, name='quiz-submit'),
    path('progress/', views.progress, name='progress'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('upload/', views.upload_lesson, name='upload_lesson'),
]
