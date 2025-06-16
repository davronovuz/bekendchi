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



from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import MidtermAssessment, MidtermTask, Student
from .forms import MidtermAssessmentForm, MidtermTaskForm

@login_required
def midtermassessment_list(request):
    assessments = MidtermAssessment.objects.select_related('student').prefetch_related('tasks').all()
    return render(request, 'midtermassessment_list.html', {'assessments': assessments})

@login_required
def midtermassessment_create(request):
    if request.method == "POST":
        form = MidtermAssessmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Nazorat ishi muvaffaqiyatli qo'shildi!")
            return redirect('midtermassessment_list')
    else:
        form = MidtermAssessmentForm()
    return render(request, 'midterm_form.html', {'form': form})

@login_required
def midtermassessment_edit(request, pk):
    assessment = get_object_or_404(MidtermAssessment, pk=pk)
    if request.method == "POST":
        form = MidtermAssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            messages.success(request, "Nazorat ishi yangilandi!")
            return redirect('midtermassessment_list')
    else:
        form = MidtermAssessmentForm(instance=assessment)
    return render(request, 'midterm_form.html', {'form': form})

@login_required
def midtermassessment_delete(request, pk):
    assessment = get_object_or_404(MidtermAssessment, pk=pk)
    if request.method == "POST":
        assessment.delete()
        messages.success(request, "Nazorat ishi o'chirildi!")
        return redirect('midtermassessment_list')
    return render(request, 'midtermassessment_confirm_delete.html', {'assessment': assessment})

# MidtermTask uchun CRUD
@login_required
def midtermtask_create(request, assessment_id):
    assessment = get_object_or_404(MidtermAssessment, pk=assessment_id)
    if request.method == "POST":
        form = MidtermTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assessment = assessment
            task.save()
            messages.success(request, "Vazifa muvaffaqiyatli qo'shildi!")
            return redirect('midtermassessment_list')
    else:
        form = MidtermTaskForm()
    return render(request, 'midtermtask_form.html', {'form': form, 'assessment': assessment})

@login_required
def midtermtask_edit(request, pk):
    task = get_object_or_404(MidtermTask, pk=pk)
    if request.method == "POST":
        form = MidtermTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Vazifa yangilandi!")
            return redirect('midtermassessment_list')
    else:
        form = MidtermTaskForm(instance=task)
    return render(request, 'midtermtask_form.html', {'form': form, 'assessment': task.assessment})

@login_required
def midtermtask_delete(request, pk):
    task = get_object_or_404(MidtermTask, pk=pk)
    if request.method == "POST":
        task.delete()
        messages.success(request, "Vazifa o'chirildi!")
        return redirect('midtermassessment_list')
    return render(request, 'midtermtask_confirm_delete.html', {'task': task})