from django.contrib import admin
from .models import Course, Lesson, LessonProgress, LabSubmission, LabAssignment, SupportMessage


class StaffOnlyAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff

@admin.register(Course)
class CourseAdmin(StaffOnlyAdmin):
    list_display = ('title', 'author', 'is_published')

@admin.register(Lesson)
class LessonAdmin(StaffOnlyAdmin):
    list_display = ('title', 'course')

@admin.register(LessonProgress)
class LessonProgressAdmin(StaffOnlyAdmin):
    list_display = ('user', 'lesson', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'user')

@admin.register(LabSubmission)
class LabSubmissionAdmin(StaffOnlyAdmin):
    list_display = ('student', 'course', 'lab_title', 'submitted_at', 'is_checked', 'grade')
    list_filter = ('is_checked', 'course', 'student')
    search_fields = ('student__username', 'lab_title')
    list_editable = ('grade', 'is_checked')

@admin.register(LabAssignment)
class LabAssignmentAdmin(StaffOnlyAdmin):
    list_display = ('title', 'course', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'description')

@admin.register(SupportMessage)
class SupportMessageAdmin(StaffOnlyAdmin):
    list_display = ('user_name', 'email', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('user_name', 'email', 'message')
    list_editable = ('is_resolved',)