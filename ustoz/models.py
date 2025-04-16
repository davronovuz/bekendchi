from django.db import models


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