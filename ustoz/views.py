from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Group, Student, Attendance


def group_list(request):
    groups = Group.objects.all()
    return render(request, 'group_list.html', {'groups': groups})


def group_attendance(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    students = group.students.all()

    # Har bir o‘quvchi uchun davomat va vazifa ma'lumotlarini tayyorlash
    attendance_data = []
    for student in students:
        attendances = student.attendances.order_by('lesson_number')
        attendance_dict = {attendance.lesson_number: attendance for attendance in attendances}
        row = {
            'student': student,
            'attendances': [attendance_dict.get(i, None) for i in range(1, 13)],
            'score': student.calculate_score(),
            'payment': student.payment  # To‘lov holatini uzatamiz
        }
        attendance_data.append(row)

    lessons = list(range(1, 13))  # 1-dan 12-gacha bo‘lgan darslar ro‘yxati

    return render(request, 'group_attendance.html', {
        'group': group,
        'attendance_data': attendance_data,
        'lessons': lessons
    })


@login_required
def update_attendance(request, group_id):
    if request.method == 'POST':
        group = get_object_or_404(Group, id=group_id)
        students = group.students.all()

        for student in students:
            for lesson in range(1, 13):
                is_present_key = f"present_{student.id}_{lesson}"
                task_completed_key = f"task_{student.id}_{lesson}"

                is_present = request.POST.get(is_present_key) == 'on'
                task_completed = request.POST.get(task_completed_key) == 'on'

                Attendance.objects.update_or_create(
                    student=student,
                    lesson_number=lesson,
                    defaults={
                        'is_present': is_present,
                        'task_completed': task_completed
                    }
                )

            # To‘lov holatini yangilash
            payment_key = f"payment_{student.id}"
            payment = request.POST.get(payment_key) == 'on'
            student.payment = payment
            student.save()

        return redirect('group_attendance', group_id=group.id)
    return redirect('group_attendance', group_id=group_id)