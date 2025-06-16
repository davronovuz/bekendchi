from django.contrib import admin
from .models import Group, Student, Attendance,MidtermAssessment, MidtermTask

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'group', 'calculate_score')
    list_filter = ('group',)
    search_fields = ('first_name', 'last_name')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson_number', 'is_present', 'task_completed')
    list_filter = ('student__group', 'lesson_number')
    search_fields = ('student__first_name', 'student__last_name')




@admin.register(MidtermAssessment)
class MidtermAssessmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'assessment_number', 'date')
    list_filter = ('assessment_number', 'date')
    search_fields = ('student__first_name', 'student__last_name')

@admin.register(MidtermTask)
class MidtermTaskAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'task_type', 'score', 'max_score')
    list_filter = ('task_type',)
    search_fields = ('assessment__student__first_name', 'assessment__student__last_name', 'task_type')