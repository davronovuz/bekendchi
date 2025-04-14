from django.db import models
from apps.account.models import User
from apps.shared.models import BaseModel

class Problem(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=[
        ('easy', 'Oson'),
        ('medium', 'O‘rta'),
        ('hard', 'Qiyin'),
    ])


    def __str__(self):
        return self.title


class TestCase(BaseModel):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField()
    expected_output = models.TextField()

    def __str__(self):
        return f"Test Case for {self.problem.title}"


class Submission(BaseModel):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='python')
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Kutilmoqda'),
        ('correct', 'To‘g‘ri'),
        ('incorrect', 'Noto‘g‘ri'),
        ('error', 'Xato'),
    ])


    def __str__(self):
        return f"{self.user.username} - {self.problem.title}"