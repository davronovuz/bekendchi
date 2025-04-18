from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.account.models import User

# Fan modeli: Musobaqada qatnashadigan fanlarni saqlaydi
class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Fanning nomi, masalan, 'Matematika'")
    description = models.TextField(blank=True, null=True, help_text="Fanning qisqa ta'rifi")
    slug = models.SlugField(max_length=100, unique=True, help_text="URL uchun qulay ID, masalan, 'matematika'")
    icon = models.CharField(max_length=50, blank=True, help_text="Fanning ikonka belgisi, masalan, emoji 📐 yoki rasm URL")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Fan"
        verbose_name_plural = "Fanlar"

# Quiz modeli: Test yoki musobaqa tuzilmasi
class Quiz(models.Model):
    DIFFICULTY_CHOICES = (
        ('oson', 'Oson'),
        ('orta', 'O‘rta'),
        ('qiyin', 'Qiyin'),
    )

    title = models.CharField(max_length=200, help_text="Quiz nomi, masalan, 'Matematika Test #1'")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes', help_text="Quiz qaysi fanga tegishli")
    description = models.TextField(blank=True, null=True, help_text="Quiz ta'rifi")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='oson', help_text="Quizning qiyinlik darajasi")
    cover_image = models.URLField(blank=True, null=True, help_text="Quiz uchun jozibali rasm URL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration = models.DurationField(blank=True, null=True, help_text="Quiz davomiyligi, masalan, 30 daqiqa")
    start_time = models.DateTimeField(blank=True, null=True, help_text="Quiz boshlanish vaqti")
    is_active = models.BooleanField(default=True, help_text="Quiz faol yoki yo‘qligi")
    max_attempts = models.PositiveIntegerField(default=1, help_text="Maksimal urinishlar soni")

    def __str__(self):
        return f"{self.title} ({self.subject.name})"

    @property
    def is_ongoing(self):
        """Quiz hozir faol yoki yo‘qligini tekshirish"""
        if not self.start_time or not self.duration:
            return self.is_active
        now = timezone.now()
        return self.is_active and self.start_time <= now <= self.start_time + self.duration

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quiz’lar"

# Savol modeli: Quiz ichidagi savollarni saqlaydi
class Question(models.Model):
    QUESTION_TYPES = (
        ('MC', 'Multiple Choice'),  # Ko‘p tanlovli
        ('SA', 'Short Answer'),    # Qisqa javob
        ('CD', 'Coding'),          # Kod yozish
    )

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', help_text="Savol qaysi quiz’ga tegishli")
    text = models.TextField(help_text="Savol matni")
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES, help_text="Savol turi")
    points = models.PositiveIntegerField(default=1, help_text="Savol uchun ball")
    time_limit = models.PositiveIntegerField(default=30, help_text="Savol uchun vaqt chegarasi (sekundlarda)")
    explanation = models.TextField(blank=True, null=True, help_text="To‘g‘ri javobning izohi")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.text[:50]}... ({self.get_question_type_display()})"

    class Meta:
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"

# Ko‘p tanlovli savollar uchun variantlar
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', help_text="Variant qaysi savolga tegishli")
    text = models.CharField(max_length=200, help_text="Javob varianti matni")
    is_correct = models.BooleanField(default=False, help_text="Bu variant to‘g‘ri yoki yo‘qligi")

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Javob varianti"
        verbose_name_plural = "Javob variantlari"

# Foydalanuvchi natijasi modeli: Quiz javoblarini saqlaydi
class QuizSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_submissions', help_text="Quiz topshirgan foydalanuvchi")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions', help_text="Topshirilgan quiz")
    submitted_at = models.DateTimeField(auto_now_add=True)
    total_score = models.PositiveIntegerField(default=0, help_text="Umumiy ball")
    correct_answers = models.PositiveIntegerField(default=0, help_text="To‘g‘ri javoblar soni")
    wrong_answers = models.PositiveIntegerField(default=0, help_text="Xato javoblar soni")
    streak = models.PositiveIntegerField(default=0, help_text="Ketma-ket to‘g‘ri javoblar soni")
    stars = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)], help_text="Yulduzlar (0-3)")
    is_completed = models.BooleanField(default=False, help_text="Quiz tugallangan yoki yo‘qligi")
    attempt_number = models.PositiveIntegerField(default=1, help_text="Urinish raqami")

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} (Attempt {self.attempt_number})"

    class Meta:
        unique_together = ('user', 'quiz', 'attempt_number')
        verbose_name = "Quiz topshirigi"
        verbose_name_plural = "Quiz topshiriklari"

# Foydalanuvchi javoblari: Har bir savolga berilgan javob
class Answer(models.Model):
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name='answers', help_text="Javob qaysi topshirikka tegishli")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', help_text="Javob berilgan savol")
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True, help_text="Ko‘p tanlovli savol uchun tanlangan variant")
    text_answer = models.TextField(blank=True, null=True, help_text="Qisqa javob yoki kod uchun matn")
    is_correct = models.BooleanField(default=False, help_text="Javob to‘g‘ri yoki yo‘qligi")
    score = models.PositiveIntegerField(default=0, help_text="Ushbu javob uchun ball")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer to {self.question.text[:20]}... by {self.submission.user.username}"

    class Meta:
        verbose_name = "Javob"
        verbose_name_plural = "Javoblar"

# Leaderboard modeli: Eng yaxshi natijalarni saqlaydi
class Leaderboard(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='leaderboard', help_text="Leaderboard qaysi quiz’ga tegishli")
    entries = models.ManyToManyField(QuizSubmission, blank=True, help_text="Eng yaxshi natijalar ro‘yxati")

    def __str__(self):
        return f"Leaderboard: {self.quiz.title}"

    class Meta:
        verbose_name = "Leaderboard"
        verbose_name_plural = "Leaderboard’lar"

# Musobaqa sozlamalari modeli: Umumiy qoidalarni saqlaydi
class QuizSettings(models.Model):
    points_per_correct = models.PositiveIntegerField(default=10, help_text="To‘g‘ri javob uchun ball")
    streak_bonus = models.PositiveIntegerField(default=5, help_text="Ketma-ket to‘g‘ri javoblar uchun bonus ball")
    max_streak = models.PositiveIntegerField(default=3, help_text="Maksimal streak chegarasi")
    star_thresholds = models.JSONField(default=dict, help_text="Yulduzlar chegarasi, masalan, {'3': 80, '2': 60, '1': 0}")

    def __str__(self):
        return "Musobaqa sozlamalari"

    class Meta:
        verbose_name = "Musobaqa sozlamasi"
        verbose_name_plural = "Musobaqa sozlamalari"

# Badge modeli: Foydalanuvchilar uchun yutuq nishonlari
class Badge(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Nishon nomi, masalan, 'Matematika Ustasi'")
    description = models.TextField(blank=True, null=True, help_text="Nishon ta'rifi")
    icon = models.CharField(max_length=50, blank=True, help_text="Nishon ikonka belgisi, masalan, emoji 🏆")
    users = models.ManyToManyField(User, blank=True, related_name='badges', help_text="Nishonni olgan foydalanuvchilar")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Nishon"
        verbose_name_plural = "Nishonlar"