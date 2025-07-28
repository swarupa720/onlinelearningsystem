from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Course, Lesson, Quiz, UserProgress

# Optional Home View
def home(request):
    return HttpResponse("Courses App Home Page")

# ✅ Course Detail View – shows progress bar and lesson list
@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course)
    total_lessons = lessons.count()

    completed_lessons = UserProgress.objects.filter(
        user=request.user,
        lesson__in=lessons,
        completed=True
    ).count()

    progress_percent = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'total': total_lessons,
        'completed': completed_lessons,
        'progress_percent': progress_percent
    })

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    all_lessons = Lesson.objects.all().order_by('id')  # or filter by course if needed
    total = all_lessons.count()

    completed = UserProgress.objects.filter(user=request.user, completed=True).count()

    if total > 0:
        progress_percent = int((completed / total) * 100)
    else:
        progress_percent = 0

    return render(request, 'courses/lesson_details.html', {
        'lesson': lesson,
        'progress_percent': progress_percent
    })

# ✅ Quiz View – only shows if lesson is marked as completed
@login_required
def quiz_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    # Check if the user completed the lesson
    progress = UserProgress.objects.filter(user=request.user, lesson=lesson).first()
    if not progress or not progress.completed:
        return render(request, 'courses/quiz_locked.html', {'lesson': lesson})

    # Load quiz questions
    questions = Quiz.objects.filter(lesson=lesson)
    return render(request, 'courses/quiz.html', {
        'lesson': lesson,
        'questions': questions
    })

# ✅ Quiz Submission View – shows score and updates progress
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

        # ✅ Mark lesson as completed
        UserProgress.objects.update_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'completed': True}
        )

        return render(request, 'courses/quiz_result.html', {
            'lesson': lesson,
            'score': score,
            'total': questions.count(),
            'results': results
        })
