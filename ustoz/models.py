from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='students')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    payment = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def calculate_score(self):
        attendances = self.attendances.all()
        total_conditions = 24  # 12 dars uchun davomat va vazifa
        total_true = 0

        for attendance in attendances:
            if attendance.is_present:
                total_true += 1
            if attendance.task_completed:
                total_true += 1

        payment_made = self.payment
        if total_true == total_conditions and payment_made:
            return 100
        else:
            score = (total_true / total_conditions) * 70
            if payment_made:
                score += 30
            return round(score, 2)


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    lesson_number = models.IntegerField()
    is_present = models.BooleanField(default=False)
    task_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.lesson_number}-dars"




class MidtermAssessment(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='midterm_assessments')
    assessment_number = models.IntegerField(
        choices=[(1, '1-nazorat'), (2, '2-nazorat'), (3, '3-nazorat'), (4, '4-nazorat'),(5, '5-nazorat'),(6, '6-nazorat')],
        help_text="Nazorat ishi raqami"
    )
    date = models.DateField()
    comment = models.CharField(max_length=200, blank=True, help_text="Nazorat ishi bo'yicha umumiy izoh")

    def __str__(self):
        return f"{self.student} - {self.get_assessment_number_display()} ({self.date})"

    class Meta:
        unique_together = ['student', 'assessment_number', 'date']
        ordering = ['date', 'assessment_number']


class MidtermTask(models.Model):
    assessment = models.ForeignKey(MidtermAssessment, on_delete=models.CASCADE, related_name='tasks')
    task_type = models.CharField(
        max_length=100,
        help_text="Vazifa turi (masalan, Test, Word amaliyoti, Excel amaliyoti)"
    )
    max_score = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Vazifa uchun maksimal ball"
    )
    score = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Talaba olgan ball"
    )
    comment = models.CharField(max_length=200, blank=True, help_text="Vazifa bo'yicha izoh")

    def __str__(self):
        return f"{self.assessment} - {self.task_type} ({self.score}/{self.max_score})"

    class Meta:
        ordering = ['assessment', 'task_type']

    def clean(self):
        if self.score > self.max_score:
            raise ValidationError("Ball maksimal balldan oshmasligi kerak.")