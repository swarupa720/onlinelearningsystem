from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, logout
from django.contrib import messages
from .models import Course, Lesson, Quiz, UserProgress
from .forms import LessonUploadForm, CourseForm, QuizForm

User = get_user_model()


def home(request):
    return HttpResponse("Courses App Home Page")


@login_required
def course_list(request):
    all_courses = Course.objects.all().prefetch_related('lesson_set')
    course_data = []

    for course in all_courses:
        lessons = course.lesson_set.all()
        total = lessons.count()
        completed_count = UserProgress.objects.filter(
            user=request.user,
            lesson__in=lessons,
            completed=True
        ).count()
        progress_percent = round((completed_count / total) * 100) if total else 0

        course_data.append({
            'course': course,
            'total': total,
            'completed': completed_count,
            'progress_percent': progress_percent
        })

    return render(request, 'courses/course_list.html', {'course_data': course_data})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course)
    total_lessons = lessons.count()

    completed_queryset = UserProgress.objects.filter(
        user=request.user,
        lesson__in=lessons,
        completed=True
    )
    completed_count = completed_queryset.count()
    completed_ids = list(completed_queryset.values_list('lesson_id', flat=True))

    progress_percent = int((completed_count / total_lessons) * 100) if total_lessons else 0

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'total': total_lessons,
        'completed': completed_count,
        'completed_ids': completed_ids,
        'progress_percent': progress_percent
    })


@login_required
def available_courses(request):
    all_courses = Course.objects.exclude(created_by=request.user).prefetch_related('lesson_set')
    # Add progress info (optional)
    course_data = []
    for course in all_courses:
        total_lessons = course.lesson_set.count()
        # You can add more info if needed
        course_data.append({
            'course': course,
            'total_lessons': total_lessons,
        })
    # If you want to pass course_data, update your template accordingly
    return render(request, 'courses/available_courses.html', {'all_courses': all_courses})


@login_required
def faculty_dashboard(request):
    """Faculty dashboard showing only their own courses."""
    my_courses = Course.objects.filter(created_by=request.user).prefetch_related('lesson_set')
    return render(request, 'users/faculty_dashboard.html', {'my_courses': my_courses})


@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    lessons = Lesson.objects.filter(course=lesson.course).order_by('id')

    lesson_ids = list(lessons.values_list('id', flat=True))
    current_index = lesson_ids.index(lesson.id)
    next_lesson = lessons[current_index + 1] if current_index + 1 < len(lesson_ids) else None

    total = lessons.count()
    completed = UserProgress.objects.filter(user=request.user, lesson__in=lessons, completed=True).count()
    progress_percent = int((completed / total) * 100) if total else 0

    return render(request, 'courses/lesson_detail.html', {
        'lesson': lesson,
        'progress_percent': progress_percent,
        'next_lesson': next_lesson
    })


@login_required
def quiz_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    questions = Quiz.objects.filter(lesson=lesson)
    return render(request, 'courses/quiz.html', {'lesson': lesson, 'questions': questions})


@login_required
def quiz_submit(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    questions = Quiz.objects.filter(lesson=lesson)

    if request.method == 'POST':
        score = 0
        results = []

        for question in questions:
            selected = request.POST.get(f'q{question.id}')
            correct = question.correct_option
            is_correct = (selected == correct)
            if is_correct:
                score += 1
            results.append({
                'question': question.question_text,
                'selected': selected,
                'correct': correct,
                'is_correct': is_correct,
            })

        UserProgress.objects.update_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'completed': True}
        )

        lessons = Lesson.objects.filter(course=lesson.course).order_by('id')
        lesson_ids = list(lessons.values_list('id', flat=True))
        current_index = lesson_ids.index(lesson.id)
        next_lesson = lessons[current_index + 1] if current_index + 1 < len(lesson_ids) else None

        return render(request, 'courses/quiz_result.html', {
            'lesson': lesson,
            'score': score,
            'total': questions.count(),
            'results': results,
            'next_lesson': next_lesson
        })

    return HttpResponse("Invalid request method", status=400)


@login_required
def progress(request):
    progress_data = UserProgress.objects.filter(user=request.user)
    return render(request, 'courses/progress.html', {'progress_data': progress_data})

@login_required
def my_courses(request):
    courses = Course.objects.filter(created_by=request.user)
    return render(request, 'courses/my_courses.html', {'courses': courses})


@login_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.created_by = request.user
            course.save()
            return redirect('courses:my_courses')
    else:
        form = CourseForm()
    return render(request, 'courses/create_course.html', {'form': form})


@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.created_by != request.user:
        return HttpResponseForbidden("❌ You are not allowed to edit this course.")
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('courses:my_courses')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/edit_course.html', {'form': form, 'course': course})


@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.created_by != request.user:
        return HttpResponseForbidden("❌ You are not allowed to delete this course.")
    if request.method == 'POST':
        course.delete()
        return redirect('courses:my_courses')
    return render(request, 'courses/confirm_delete.html', {'course': course})


@login_required
def upload_lesson(request):
    if request.method == 'POST':
        form = LessonUploadForm(request.POST, user=request.user)
        if form.is_valid():
            lesson = form.save(commit=False)
            # Double check: only allow adding to courses owned by the user
            if lesson.course.created_by != request.user:
                return HttpResponseForbidden("❌ You cannot add lessons to another faculty's course.")
            lesson.save()
            return redirect('courses:my_courses')
    else:
        form = LessonUploadForm(user=request.user)
    return render(request, 'courses/upload_lesson.html', {'form': form})


@login_required
def add_quiz(request, lesson_id=None):
    lesson = None
    quizzes = None
    if lesson_id:
        lesson = get_object_or_404(
            Lesson.objects.select_related('course'),
            id=lesson_id,
            course__created_by=request.user
        )
        quizzes = Quiz.objects.filter(lesson=lesson)

    if request.method == 'POST':
        form = QuizForm(request.POST, user=request.user)
        if form.is_valid():
            quiz = form.save(commit=False)
            if lesson:
                quiz.lesson = lesson
            quiz.save()
            return redirect('courses:add_quiz', lesson_id=lesson.id)
    else:
        form = QuizForm(user=request.user)
    
    return render(request, 'courses/add_quiz.html', {
        'form': form,
        'lesson': lesson,
        'quizzes': quizzes,
    })


@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if lesson.course.created_by != request.user:
        return HttpResponseForbidden("❌ You are not allowed to delete this lesson.")
    if request.method == 'POST':
        course_id = lesson.course.id
        lesson.delete()
        return redirect('courses:course-detail', course_id=course_id)
    return render(request, 'courses/confirm_delete_lesson.html', {'lesson': lesson})


@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if quiz.lesson.course.created_by != request.user:
        return HttpResponseForbidden("❌ You are not allowed to delete this quiz question.")
    if request.method == 'POST':
        lesson_id = quiz.lesson.id
        quiz.delete()
        return redirect('courses:add_quiz', lesson_id=lesson_id)
    return render(request, 'courses/confirm_delete_quiz.html', {'quiz': quiz})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "✅ You have successfully logged out.")
    return redirect('login')
