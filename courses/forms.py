# courses/forms.py
from django import forms
from .models import Lesson

class LessonUploadForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['course', 'title', 'video_url']
