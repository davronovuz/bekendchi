from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='students')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def calculate_score(self):
        # Davomat va vazifa bajarilganliklarini olish
        attendances = self.attendances.all()  # 12 dars uchun
        total_conditions = 24  # 12 dars * (davomat + vazifa)

        # Barcha True qiymatlarni hisoblash
        total_true = 0
        for attendance in attendances:
            if attendance.is_present:
                total_true += 1
            if attendance.task_completed:
                total_true += 1

        # Oxirgi darsning vazifasi bajarilganmi?
        last_attendance = attendances.last()
        last_task_completed = last_attendance.task_completed if last_attendance else False

        # Formula bo‘yicha hisoblash
        if total_true == total_conditions and last_task_completed:
            return 100
        else:
            score = (total_true / total_conditions) * 70
            if last_task_completed:
                score += 30
            return round(score, 2)

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    lesson_number = models.IntegerField(choices=[(i, f"{i}-dars") for i in range(1, 13)])
    is_present = models.BooleanField(default=False)  # Davomat
    task_completed = models.BooleanField(default=False)  # Vazifa bajarilganmi

    def __str__(self):
        return f"{self.student} - {self.lesson_number}-dars"

    class Meta:
        unique_together = ('student', 'lesson_number')  # Har bir o‘quvchi uchun har bir dars faqat bir marta bo‘ladi