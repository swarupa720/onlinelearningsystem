from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Course, Lesson, Quiz, UserProgress

# ✅ Home View (optional)
def home(request):
    return HttpResponse("Courses App Home Page")

# ✅ Course List View
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

# ✅ Course Detail View
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

    progress_percent = int((completed_count / total_lessons) * 100) if total_lessons > 0 else 0

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'total': total_lessons,
        'completed': completed_count,
        'completed_ids': completed_ids,
        'progress_percent': progress_percent
    })

# ✅ Lesson Detail View
@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    lessons = Lesson.objects.filter(course=lesson.course).order_by('id')

    lesson_ids = list(lessons.values_list('id', flat=True))
    current_index = lesson_ids.index(lesson.id)

    next_lesson = lessons[current_index + 1] if current_index + 1 < len(lesson_ids) else None

    total = lessons.count()
    completed = UserProgress.objects.filter(user=request.user, lesson__in=lessons, completed=True).count()
    progress_percent = int((completed / total) * 100) if total > 0 else 0

    return render(request, 'courses/lesson_detail.html', {
        'lesson': lesson,
        'progress_percent': progress_percent,
        'next_lesson': next_lesson
    })

# ✅ Quiz View
@login_required
def quiz_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    questions = Quiz.objects.filter(lesson=lesson)

    return render(request, 'courses/quiz.html', {
        'lesson': lesson,
        'questions': questions,
    })

# ✅ Quiz Submission View
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

        # Mark lesson as completed
        UserProgress.objects.update_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'completed': True}
        )

        # Determine next lesson
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
