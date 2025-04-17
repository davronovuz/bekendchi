from django.db import models
from apps.account.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

# Contest modeli
class Contest(models.Model):
    title = models.CharField(max_length=200, verbose_name="Contest Nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    start_time = models.DateTimeField(verbose_name="Boshlanish Vaqti")
    end_time = models.DateTimeField(verbose_name="Tugash Vaqti")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan Vaqt")

    class Meta:
        verbose_name = "Contest"
        verbose_name_plural = "Contests"

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        return self.start_time <= now <= self.end_time and self.is_active

# Problem modeli
class Problem(models.Model):
    DIFFICULTY_CHOICES = (
        (1, "Oson"),
        (2, "O‘rta"),
        (3, "Qiyin"),
    )

    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="problems", verbose_name="Contest")
    title = models.CharField(max_length=200, verbose_name="Masala Nomi")
    description = models.TextField(verbose_name="Masala Tavsifi")
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=1, verbose_name="Daraja")
    time_limit = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(60)], verbose_name="Vaqt Limiti (sekund)")
    points = models.IntegerField(default=100, validators=[MinValueValidator(10)], verbose_name="Ball")
    input_example = models.TextField(blank=True, verbose_name="Kirish Misoli")
    output_example = models.TextField(blank=True, verbose_name="Chiqish Misoli")
    test_cases_input = models.TextField(blank=True, verbose_name="Test Case Kirishlari")
    test_cases_output = models.TextField(blank=True, verbose_name="Test Case Chiqishlari")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan Vaqt")

    class Meta:
        verbose_name = "Masala"
        verbose_name_plural = "Masalalar"

    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"

# Submission modeli
class Submission(models.Model):
    STATUS_CHOICES = (
        ('PENDING', "Kutilmoqda"),
        ('ACCEPTED', "Qabul Qilindi"),
        ('WRONG_ANSWER', "Noto‘g‘ri Javob"),
        ('TIME_LIMIT_EXCEEDED', "Vaqt Limitidan Oshdi"),
        ('ERROR', "Xatolik"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions", verbose_name="Foydalanuvchi")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="submissions", verbose_name="Masala")
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="submissions", verbose_name="Contest")
    code = models.TextField(verbose_name="Yuborilgan Kod")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING", verbose_name="Holati")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan Vaqt")
    execution_time = models.FloatField(null=True, blank=True, verbose_name="Ishlash Vaqti (sekund)")

    class Meta:
        verbose_name = "Yuborilgan Kod"
        verbose_name_plural = "Yuborilgan Kodlar"

    def __str__(self):
        return f"{self.user.username} - {self.problem.title} ({self.status})"

# ContestParticipant modeli (Leaderboard va Online holat uchun)
class ContestParticipant(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="participants", verbose_name="Contest")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contest_participations", verbose_name="Foydalanuvchi")
    total_score = models.IntegerField(default=0, verbose_name="Umumiy Ball")
    problems_solved = models.IntegerField(default=0, verbose_name="Yechilgan Masalalar Soni")
    last_submission = models.DateTimeField(null=True, blank=True, verbose_name="Oxirgi Yuborish")
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name="Oxirgi Faollik")  # Online holatni aniqlash uchun

    class Meta:
        verbose_name = "Contest Ishtirokchisi"
        verbose_name_plural = "Contest Ishtirokchilari"
        unique_together = ('contest', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.contest.title} ({self.total_score} ball)"

    @property
    def is_online(self):
        if not self.last_activity:
            return False
        now = datetime.datetime.now(datetime.timezone.utc)
        time_difference = (now - self.last_activity).total_seconds()
        return time_difference <= 300  # 5 daqiqa (300 sekund) ichida faol bo‘lsa online deb hisoblanadi

    @property
    def submission_count(self):
        return Submission.objects.filter(user=self.user, contest=self.contest).count()