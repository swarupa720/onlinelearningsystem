# courses/forms.py

from django import forms
from .models import Course, Lesson, Quiz

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']  # 'created_by' will be set in the view


class LessonUploadForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['course', 'title', 'video_url']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # get the logged-in user
        super().__init__(*args, **kwargs)
        if user:
            # Limit course list to only those created by this faculty
            self.fields['course'].queryset = Course.objects.filter(created_by=user)


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = [
            'lesson',
            'question_text',
            'option_a',
            'option_b',
            'option_c',
            'option_d',
            'correct_option'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the logged-in faculty user
        super().__init__(*args, **kwargs)
        if user:
            # Limit lessons to those belonging to courses created by this faculty
            self.fields['lesson'].queryset = Lesson.objects.filter(course__created_by=user)
