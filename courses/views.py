from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from .models import Course, Lesson, Quiz, UserProgress, Enrollment
from .forms import LessonUploadForm, CourseForm, QuizForm
from .utils import has_completed_course, generate_certificate
from django.contrib.auth.decorators import login_required

# ------------------------
# Helpers
# ------------------------
def is_student(user):
    return user.groups.filter(name="Students").exists()


# ------------------------
# Student: Available + Enroll + My Courses
# ------------------------
def available_courses(request):
    """Show courses student has not enrolled in yet."""
    if request.user.is_authenticated:
        enrolled_courses = Enrollment.objects.filter(student=request.user).values_list("course_id", flat=True)
        courses = Course.objects.exclude(id__in=enrolled_courses).exclude(created_by=request.user)
    else:
        courses = Course.objects.all()
    return render(request, "courses/available_courses.html", {"all_courses": courses})


def enroll_course(request, course_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to enroll.")
        return redirect("login")

    course = get_object_or_404(Course, id=course_id)

    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)

    if created:
        messages.success(request, f"✅ You are enrolled in {course.title}!")
    else:
        messages.info(request, f"ℹ You are already enrolled in {course.title}.")
    return redirect('courses:my_courses')


@login_required
def my_courses(request):
    user = request.user

    # Courses uploaded by faculty
    uploaded_courses = Course.objects.filter(created_by=user) if getattr(user, "is_faculty", False) else []

    # Courses enrolled by student
    enrolled_courses = [e.course for e in Enrollment.objects.filter(student=user)] if getattr(user, "is_student", False) else []

    context = {
        "uploaded_courses": uploaded_courses,
        "enrolled_courses": enrolled_courses,
    }
    return render(request, "courses/my_courses.html", context)
# ------------------------
# Course Views
# ------------------------
def course_list(request):
    all_courses = Course.objects.all().prefetch_related("lesson_set")
    course_data = []

    for course in all_courses:
        lessons = course.lesson_set.all()
        total = lessons.count()
        if request.user.is_authenticated:
            completed_count = UserProgress.objects.filter(user=request.user, lesson__in=lessons, completed=True).count()
        else:
            completed_count = 0
        progress_percent = round((completed_count / total) * 100) if total else 0

        course_data.append({
            "course": course,
            "total": total,
            "completed": completed_count,
            "progress_percent": progress_percent
        })

    return render(request, "courses/course_list.html", {"course_data": course_data})


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course)
    total_lessons = lessons.count()

    if request.user.is_authenticated:
        completed_queryset = UserProgress.objects.filter(user=request.user, lesson__in=lessons, completed=True)
        completed_count = completed_queryset.count()
        completed_ids = list(completed_queryset.values_list("lesson_id", flat=True))
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        course_completed = has_completed_course(request.user, course)
    else:
        completed_count = 0
        completed_ids = []
        is_enrolled = False
        course_completed = False

    progress_percent = int((completed_count / total_lessons) * 100) if total_lessons else 0

    return render(request, "courses/course_detail.html", {
        "course": course,
        "lessons": lessons,
        "total": total_lessons,
        "completed": completed_count,
        "completed_ids": completed_ids,
        "progress_percent": progress_percent,
        "is_enrolled": is_enrolled,
        "course_completed": course_completed,
    })


# ------------------------
# Lesson + Quiz
# ------------------------
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    lessons = Lesson.objects.filter(course=lesson.course).order_by("id")
    lesson_ids = list(lessons.values_list("id", flat=True))
    current_index = lesson_ids.index(lesson.id)
    next_lesson = lessons[current_index + 1] if current_index + 1 < len(lesson_ids) else None

    if request.user.is_authenticated:
        total = lessons.count()
        completed = UserProgress.objects.filter(user=request.user, lesson__in=lessons, completed=True).count()
        progress_percent = int((completed / total) * 100) if total else 0
    else:
        progress_percent = 0

    return render(request, "courses/lesson_detail.html", {
        "lesson": lesson,
        "progress_percent": progress_percent,
        "next_lesson": next_lesson
    })


def quiz_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    questions = Quiz.objects.filter(lesson=lesson)
    return render(request, "courses/quiz.html", {"lesson": lesson, "questions": questions})


def quiz_submit(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    questions = Quiz.objects.filter(lesson=lesson)

    if request.method == "POST" and request.user.is_authenticated:
        score = 0
        results = []

        for question in questions:
            selected = request.POST.get(f"q{question.id}")
            is_correct = (selected == question.correct_option)
            if is_correct:
                score += 1
            results.append({
                "question": question.question_text,
                "selected": selected,
                "correct": question.correct_option,
                "is_correct": is_correct,
            })

        UserProgress.objects.update_or_create(
            user=request.user,
            lesson=lesson,
            defaults={"completed": True}
        )

        lessons = Lesson.objects.filter(course=lesson.course).order_by("id")
        lesson_ids = list(lessons.values_list("id", flat=True))
        current_index = lesson_ids.index(lesson.id)
        next_lesson = lessons[current_index + 1] if current_index + 1 < len(lesson_ids) else None

        return render(request, "courses/quiz_result.html", {
            "lesson": lesson,
            "score": score,
            "total": questions.count(),
            "results": results,
            "next_lesson": next_lesson
        })

    return HttpResponse("Invalid request method", status=400)


# ------------------------
# Progress
# ------------------------
def progress(request):
    if request.user.is_authenticated:
        progress_data = UserProgress.objects.filter(user=request.user)
    else:
        progress_data = []
    return render(request, "courses/progress.html", {"progress_data": progress_data})


# ------------------------
# Faculty: Create/Edit/Delete Course
# ------------------------
def my_uploaded_courses(request):
    if request.user.is_authenticated:
        uploaded_courses = Course.objects.filter(created_by=request.user)
    else:
        uploaded_courses = []
    return render(request, "courses/my_courses.html", {"uploaded_courses": uploaded_courses})


def create_course(request):
    if request.method == "POST" and request.user.is_authenticated:
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.created_by = request.user
            course.save()
            return redirect("courses:my_courses")
    else:
        form = CourseForm()
    return render(request, "courses/create_course.html", {"form": form})


def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user != course.created_by:
        return HttpResponseForbidden("❌ You are not allowed to edit this course.")

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("courses:my_courses")
    else:
        form = CourseForm(instance=course)

    return render(request, "courses/edit_course.html", {"form": form, "course": course})


def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user != course.created_by:
        return HttpResponseForbidden("❌ You are not allowed to delete this course.")

    if request.method == "POST":
        course.delete()
        return redirect("courses:my_courses")

    return render(request, "courses/confirm_delete.html", {"course": course})


# ------------------------
# Lessons + Quizzes (faculty side)
# ------------------------
def upload_lesson(request):
    if request.method == "POST":
        form = LessonUploadForm(request.POST, user=request.user)
        if form.is_valid():
            lesson = form.save(commit=False)
            if lesson.course.created_by != request.user:
                return HttpResponseForbidden("❌ You cannot add lessons to another faculty's course.")
            lesson.save()
            return redirect("courses:my_courses")
    else:
        form = LessonUploadForm(user=request.user)
    return render(request, "courses/upload_lesson.html", {"form": form})


def add_quiz(request, lesson_id=None):
    lesson = None
    quizzes = None
    if lesson_id:
        lesson = get_object_or_404(Lesson.objects.select_related("course"), id=lesson_id)
        quizzes = Quiz.objects.filter(lesson=lesson)

    if request.method == "POST":
        form = QuizForm(request.POST, user=request.user)
        if form.is_valid():
            quiz = form.save(commit=False)
            if lesson:
                quiz.lesson = lesson
            quiz.save()
            return redirect("courses:add_quiz", lesson_id=lesson.id)
    else:
        form = QuizForm(user=request.user)

    return render(request, "courses/add_quiz.html", {
        "form": form,
        "lesson": lesson,
        "quizzes": quizzes,
    })


def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.user != lesson.course.created_by:
        return HttpResponseForbidden("❌ You are not allowed to delete this lesson.")

    if request.method == "POST":
        course_id = lesson.course.id
        lesson.delete()
        return redirect("courses:course-detail", course_id=course_id)

    return render(request, "courses/confirm_delete_lesson.html", {"lesson": lesson})


def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.user != quiz.lesson.course.created_by:
        return HttpResponseForbidden("❌ You are not allowed to delete this quiz question.")

    if request.method == "POST":
        lesson_id = quiz.lesson.id
        quiz.delete()
        return redirect("courses:add_quiz", lesson_id=lesson_id)

    return render(request, "courses/confirm_delete_quiz.html", {"quiz": quiz})


# ------------------------
# Certificate
# ------------------------
def download_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not request.user.is_authenticated or not has_completed_course(request.user, course):
        return HttpResponse("You have not completed this course yet or are not logged in.", status=403)

    buffer = generate_certificate(
        student_name=request.user.get_full_name() or request.user.username,
        course_name=course.title
    )

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{course.title}_certificate.pdf"'
    return response


# ------------------------
# Public Home
# ------------------------
def home(request):
    return HttpResponse("Courses App Home Page")
