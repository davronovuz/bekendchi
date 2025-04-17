from django.contrib import admin
from .models import Contest, Problem, Submission, ContestParticipant

# Problem Inline (Contest ichida masalalarni ko‘rsatish uchun)
class ProblemInline(admin.TabularInline):
    model = Problem
    extra = 1  # Yangi qo‘shish uchun 1 ta bo‘sh forma
    fields = ('title', 'description', 'difficulty', 'time_limit', 'points', 'input_example', 'output_example')
    readonly_fields = ('created_at',)

# Contest Admin
@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'is_active', 'created_at', 'is_ongoing', 'participant_count')
    list_filter = ('is_active', 'start_time', 'end_time')
    search_fields = ('title',)
    inlines = [ProblemInline]
    date_hierarchy = 'start_time'
    list_per_page = 20

    # Qo‘shimcha funksiyalar
    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = "Ishtirokchilar Soni"

    # Actions: Contestni faol/faqol qilish
    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Tanlangan contestlarni faol qilish"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Tanlangan contestlarni faol emas qilish"

# Problem Admin
@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'contest', 'difficulty', 'time_limit', 'points', 'created_at')
    list_filter = ('difficulty', 'contest')
    search_fields = ('title',)
    list_per_page = 20

    # Darajani chiroyli ko‘rsatish
    def get_difficulty(self, obj):
        return obj.get_difficulty_display()
    get_difficulty.short_description = "Daraja"

# Submission Admin
@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'contest', 'status', 'submitted_at', 'execution_time')
    list_filter = ('status', 'contest', 'user')
    search_fields = ('user__username', 'problem__title')
    list_per_page = 20
    readonly_fields = ('submitted_at', 'execution_time')

    # Kodning qisqartirilgan ko‘rinishi
    def code_snippet(self, obj):
        return obj.code[:50] + "..." if len(obj.code) > 50 else obj.code
    code_snippet.short_description = "Kod (Qisqa)"

# ContestParticipant Admin
@admin.register(ContestParticipant)
class ContestParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'contest', 'total_score', 'problems_solved', 'submission_count', 'is_online', 'last_activity')
    list_filter = ('contest',)
    search_fields = ('user__username', 'contest__title')
    list_per_page = 20
    readonly_fields = ('last_submission', 'last_activity')

    # Online holatini ko‘rsatish
    def is_online(self, obj):
        return obj.is_online
    is_online.boolean = True
    is_online.short_description = "Online"

    # Submission sonini ko‘rsatish
    def submission_count(self, obj):
        return obj.submission_count
    submission_count.short_description = "Submission Soni"

    # Filtr: Online bo‘lganlarni ko‘rsatish
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'contest')