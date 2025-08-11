from django.contrib import admin
from .models import Course, Lesson, UserProgress, Quiz, CompletedQuiz, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by')
    search_fields = ('title', 'description')
    list_filter = ('created_by',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    search_fields = ('title', 'content')
    list_filter = ('course',)

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed')
    list_filter = ('completed', 'lesson')
    search_fields = ('user__username', 'lesson__title')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'question_text', 'correct_option')
    search_fields = ('question_text',)
    list_filter = ('lesson',)

@admin.register(CompletedQuiz)
class CompletedQuizAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed_at')
    list_filter = ('completed_at', 'lesson')
    search_fields = ('user__username', 'lesson__title')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_on')
    list_filter = ('enrolled_on', 'course')
    search_fields = ('student__username', 'course__title')
