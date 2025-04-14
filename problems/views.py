from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Problem, TestCase, Submission

def problem_list(request):
    problems = Problem.objects.all()
    return render(request, 'problems/problem_list.html', {'problems': problems})

def problem_detail(request, pk):
    problem = get_object_or_404(Problem, pk=pk)
    test_cases = problem.test_cases.all()
    submission = None
    if request.user.is_authenticated:
        submission = Submission.objects.filter(user=request.user, problem=problem).first()
    return render(request, 'problems/problem_detail.html', {
        'problem': problem,
        'test_cases': test_cases,
        'submission': submission
    })

@login_required
def submit_code(request, pk):
    problem = get_object_or_404(Problem, pk=pk)
    if request.method == 'POST':
        code = request.POST.get('code')
        language = request.POST.get('language')
        submission = Submission.objects.create(
            user=request.user,
            problem=problem,
            code=code,
            language=language,
            status='pending'
        )
        # Hozircha kodni tekshirish qismini keyinroq qo‘shamiz
        return redirect('problem_detail', pk=problem.pk)
    return redirect('problem_detail', pk=problem.pk)