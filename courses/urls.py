from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.lesson_detail, name='lesson_detail'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_completed, name='mark_lesson_completed'),
    path('analytics/', views.teacher_analytics, name='teacher_analytics'),
    path('teacher/course/<int:course_id>/', views.teacher_course_dashboard, name='teacher_course_dashboard'),
    path('support/submit/', views.submit_support, name='submit_support'),
]
