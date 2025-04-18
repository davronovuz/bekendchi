from django.contrib import admin
from django.utils.html import format_html
from .models import Subject, Quiz, Question, Choice, QuizSubmission, Answer, Leaderboard, QuizSettings, Badge


# Inline modellar
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text', 'question_type', 'points', 'time_limit', 'explanation')
    show_change_link = True


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    fields = ('text', 'is_correct')


# Subject admin
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_display', 'description', 'quiz_count')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20

    def quiz_count(self, obj):
        return obj.quizzes.count()
    quiz_count.short_description = 'Quiz’lar soni'

    def icon_display(self, obj):
        if obj.icon:
            return format_html('<span style="font-size: 1.5rem;">{}</span>', obj.icon)
        return '-'
    icon_display.short_description = 'Ikonka'


# Quiz admin
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'difficulty', 'is_active', 'start_time', 'duration', 'is_ongoing', 'participant_count')
    list_filter = ('subject', 'is_active', 'difficulty')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]
    actions = ['make_active', 'make_inactive']
    list_per_page = 20

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Tanlangan quiz’lar faol qilindi.")
    make_active.short_description = "Tanlangan quiz’larni faol qilish"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Tanlangan quiz’lar faol emas qilindi.")
    make_inactive.short_description = "Tanlangan quiz’larni faol emas qilish"

    def participant_count(self, obj):
        return obj.submissions.count()
    participant_count.short_description = 'Ishtirokchilar'


# Question admin
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'quiz_title', 'question_type_display', 'points', 'time_limit', 'choice_count')
    list_filter = ('quiz__subject', 'question_type')
    search_fields = ('text', 'explanation')
    inlines = [ChoiceInline]
    list_per_page = 20
    list_select_related = ('quiz',)

    def text_short(self, obj):
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    text_short.short_description = 'Savol matni'

    def quiz_title(self, obj):
        return obj.quiz.title
    quiz_title.short_description = 'Quiz'
    quiz_title.admin_order_field = 'quiz__title'

    def question_type_display(self, obj):
        types = {'MC': 'Ko‘p tanlovli', 'SA': 'Qisqa javob', 'CD': 'Kod yozish'}
        color = {'MC': '#00adb5', 'SA': '#28a745', 'CD': '#dc3545'}
        return format_html(
            '<span style="color: {};">{}</span>',
            color.get(obj.question_type, '#00adb5'),
            types.get(obj.question_type, obj.question_type)
        )
    question_type_display.short_description = 'Savol turi'
    question_type_display.admin_order_field = 'question_type'

    def choice_count(self, obj):
        return obj.choices.count()
    choice_count.short_description = 'Javoblar soni'
    choice_count.admin_order_field = 'choices__count'


# Choice admin
@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'question', 'is_correct')
    list_filter = ('question__quiz__subject', 'is_correct')
    search_fields = ('text',)
    list_per_page = 20

    def text_short(self, obj):
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    text_short.short_description = 'Javob matni'


# QuizSubmission admin
@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'total_score', 'correct_answers', 'wrong_answers', 'streak_display', 'stars_display', 'attempt_number', 'submitted_at')
    list_filter = ('quiz__subject', 'is_completed', 'submitted_at')
    search_fields = ('user__username', 'quiz__title')
    actions = ['reset_attempts']
    readonly_fields = ('submitted_at',)
    list_per_page = 20

    def reset_attempts(self, request, queryset):
        for submission in queryset:
            submission.attempt_number = 1
            submission.is_completed = False
            submission.save()
        self.message_user(request, "Tanlangan topshiriklar nollanildi.")
    reset_attempts.short_description = "Urinishlarni nollash"

    def streak_display(self, obj):
        return format_html('<span style="color: #00adb5;">{}</span>', obj.streak or 0)
    streak_display.short_description = 'Streak'

    def stars_display(self, obj):
        stars = ''.join(['⭐' for _ in range(obj.stars or 0)])
        return format_html('<span>{}</span>', stars or '-')
    stars_display.short_description = 'Yulduzlar'


# Answer admin
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('submission', 'question_short', 'is_correct', 'score', 'submitted_at')
    list_filter = ('question__quiz__subject', 'is_correct')
    search_fields = ('question__text',)
    readonly_fields = ('submitted_at',)
    list_per_page = 20

    def question_short(self, obj):
        return obj.question.text[:50] + ('...' if len(obj.question.text) > 50 else '')
    question_short.short_description = 'Savol'


# Leaderboard admin
@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'entry_count', 'top_user')
    filter_horizontal = ('entries',)
    list_per_page = 20

    def entry_count(self, obj):
        return obj.entries.count()
    entry_count.short_description = 'Natijalar soni'

    def top_user(self, obj):
        top_entry = obj.entries.order_by('-total_score', '-correct_answers').first()
        if top_entry:
            return top_entry.user.username
        return '-'
    top_user.short_description = 'Top foydalanuvchi'


# QuizSettings admin
@admin.register(QuizSettings)
class QuizSettingsAdmin(admin.ModelAdmin):
    list_display = ('points_per_correct', 'streak_bonus', 'max_streak')
    list_editable = ('streak_bonus', 'max_streak')
    list_display_links = None

    def has_add_permission(self, request):
        # Faqat bitta QuizSettings obyekti bo‘lishi uchun
        return not QuizSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # O‘chirishni taqiqlash
        return False


# Badge admin
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_display', 'description', 'user_count', 'created_at')
    filter_horizontal = ('users',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    list_per_page = 20

    def icon_display(self, obj):
        if obj.icon:
            return format_html('<span style="font-size: 1.5rem;">{}</span>', obj.icon)
        return '-'
    icon_display.short_description = 'Ikonka'

    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = 'Foydalanuvchilar soni'