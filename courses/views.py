from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Lesson, LessonProgress, LabSubmission, LabAssignment
from .forms import LabSubmissionForm
from .models import SupportMessage


def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})


def lesson_detail(request, course_id):

    course = get_object_or_404(Course, id=course_id)
    all_lessons = course.lessons.all().order_by('id')

    lesson_id = request.GET.get('lesson')
    if lesson_id:
        lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    else:
        lesson = all_lessons.first()

    return render(request, 'courses/lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'all_lessons': all_lessons
    })


@login_required
def student_dashboard(request):

    courses = Course.objects.all()
    courses_data = []

    for course in courses:
        total_lessons = course.lessons.count()

        if total_lessons > 0:
            completed_lessons = LessonProgress.objects.filter(
                user=request.user,
                lesson__course=course,
                is_completed=True
            ).count()
            progress_percent = int((completed_lessons / total_lessons) * 100)
        else:
            completed_lessons = 0
            progress_percent = 0

        courses_data.append({
            'course': course,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percent': progress_percent
        })

    if request.method == 'POST':
        form = LabSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = request.user
            submission.save()
            return redirect('student_dashboard')
    else:
        form = LabSubmissionForm()

    my_submissions = LabSubmission.objects.filter(student=request.user).order_by('-submitted_at')

    assignments = LabAssignment.objects.all().order_by('-created_at')

    return render(request, 'courses/student_dashboard.html', {
        'courses_data': courses_data,
        'form': form,
        'my_submissions': my_submissions,
        'assignments': assignments  # ДОДАЛИ ЦЕЙ РЯДОК
    })


@login_required
def mark_lesson_completed(request, lesson_id):

    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)

        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'is_completed': True}
        )

        if not progress.is_completed:
            progress.is_completed = True
            progress.save()

        return JsonResponse({'status': 'success', 'message': 'Прогрес збережено!'})

    return JsonResponse({'status': 'error', 'message': 'Тільки POST запити'}, status=400)


@login_required
def teacher_analytics(request):

    students = User.objects.filter(is_staff=False, is_superuser=False)
    courses = Course.objects.all()
    analytics_data = []


    for student in students:
        student_courses_progress = []
        for course in courses:
            total_lessons = course.lessons.count()
            if total_lessons > 0:
                completed = LessonProgress.objects.filter(
                    user=student,
                    lesson__course=course,
                    is_completed=True
                ).count()
                progress_percent = int((completed / total_lessons) * 100)
            else:
                progress_percent = 0

            student_courses_progress.append({
                'course_title': course.title,
                'percent': progress_percent
            })

        analytics_data.append({
            'student': student,
            'progress': student_courses_progress
        })


    if request.method == 'POST' and 'grade_submission' in request.POST:
        submission_id = request.POST.get('submission_id')
        grade = request.POST.get('grade')
        comment = request.POST.get('comment')

        submission = get_object_or_404(LabSubmission, id=submission_id)
        submission.grade = grade
        submission.teacher_comment = comment
        submission.is_checked = True
        submission.save()

        return redirect('teacher_analytics')


    all_submissions = LabSubmission.objects.all().order_by('-submitted_at')

    return render(request, 'courses/teacher_analytics.html', {
        'analytics_data': analytics_data,
        'courses': courses,
        'all_submissions': all_submissions,
    })


@login_required
def teacher_course_dashboard(request, course_id):

    course = get_object_or_404(Course, id=course_id)
    inclusivity_index = course.calculate_inclusivity_index()

    if request.method == 'POST' and 'publish_course' in request.POST:
        try:
            course.is_published = True
            course.save()
            return redirect('teacher_course_dashboard', course_id=course.id)
        except ValidationError as e:
            error_message = e.messages[0]
            course.is_published = False
            return render(request, 'courses/teacher_course_dashboard.html', {
                'course': course,
                'i_inc': inclusivity_index,
                'error': error_message
            })

    return render(request, 'courses/teacher_course_dashboard.html', {
        'course': course,
        'i_inc': inclusivity_index,
    })


def submit_support(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            SupportMessage.objects.create(
                user_name=name,
                email=email,
                message=message
            )

    return redirect(request.META.get('HTTP_REFERER', '/'))