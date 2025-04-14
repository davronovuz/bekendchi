from django.contrib import admin
from .models import Problem, TestCase, Submission

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'created_at')
    list_filter = ('difficulty',)
    search_fields = ('title', 'description')

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('problem', 'input_data', 'expected_output')
    list_filter = ('problem',)
    search_fields = ('input_data', 'expected_output')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'status')
    list_filter = ('status', 'problem')
    search_fields = ('user__username', 'problem__title')

