from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Public Course Views
    path('', views.course_list, name='course_list'),  # Courses home/list page
    path('available-courses/', views.available_courses, name='available_courses'),  # Other courses

    # Course Specific
    path('course/<int:course_id>/', views.course_detail, name='course-detail'),
    path('course/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('course/<int:course_id>/delete/', views.delete_course, name='delete_course'),

    # Lessons
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson-detail'),
    path('lesson/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    path('upload/', views.upload_lesson, name='upload_lesson'),

    # Quiz Related
    path('lesson/<int:lesson_id>/add-quiz/', views.add_quiz, name='add_quiz'),
    path('lesson/<int:lesson_id>/quiz/', views.quiz_view, name='quiz'),
    path('lesson/<int:lesson_id>/quiz/submit/', views.quiz_submit, name='quiz-submit'),
    path('quiz/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),

    # User Progress and Dashboard
    path('progress/', views.progress, name='progress'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),

    # Course creation
    path('create-course/', views.create_course, name='create_course'),
]
