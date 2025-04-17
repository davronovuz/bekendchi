from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json
from .models import Contest, Problem, Submission, ContestParticipant
from .forms import CodeSubmissionForm
from .utils import check_submission


def contest_list(request):
    contests = Contest.objects.all()
    return render(request, 'contest/contest_list.html', {'contests': contests})


@login_required
def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)

    # Foydalanuvchi faolligini yangilash
    participant, created = ContestParticipant.objects.get_or_create(
        contest=contest,
        user=request.user,
        defaults={'last_activity': timezone.now()}
    )
    if not created:
        participant.last_activity = timezone.now()
        participant.save()

    # Masalalarni pagination qilish
    problems = contest.problems.all()
    paginator = Paginator(problems, 10)  # Har sahifada 10 ta masala
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'contest/contest_detail.html', {
        'contest': contest,
        'page_obj': page_obj,
    })


@login_required
def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    contest = problem.contest

    # Foydalanuvchi faolligini yangilash
    participant, created = ContestParticipant.objects.get_or_create(
        contest=contest,
        user=request.user,
        defaults={'last_activity': timezone.now()}
    )
    if not created:
        participant.last_activity = timezone.now()
        participant.save()

    submissions = Submission.objects.filter(user=request.user, problem=problem)
    return render(request, 'contest/problem_detail.html', {
        'problem': problem,
        'contest': contest,
        'submissions': submissions,
        'can_submit': contest.is_ongoing,
    })


@login_required
@csrf_exempt
def submit_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code')
        problem_id = data.get('problem_id')

        problem = get_object_or_404(Problem, id=problem_id)
        contest = problem.contest

        # Contest yakunlangan bo‘lsa, kod yuborishni bloklash
        if not contest.is_ongoing:
            return JsonResponse({
                'error': 'Contest yakunlangan. Yangi yechim yuborish mumkin emas.'
            }, status=403)

        # Submission yaratish
        submission = Submission(
            user=request.user,
            problem=problem,
            contest=contest,
            code=code,
        )
        submission.save()

        # Kodni tekshirish va test case natijalarini olish
        test_results = check_submission(submission)

        # Natijani qaytarish
        return JsonResponse({
            'status': submission.status,
            'execution_time': submission.execution_time,
            'code': submission.code,
            'test_results': test_results,
        })


@login_required
def leaderboard(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)

    # Foydalanuvchi faolligini yangilash
    participant, created = ContestParticipant.objects.get_or_create(
        contest=contest,
        user=request.user,
        defaults={'last_activity': timezone.now()}
    )
    if not created:
        participant.last_activity = timezone.now()
        participant.save()

    # Leaderboard uchun pagination
    participants = ContestParticipant.objects.filter(contest=contest).order_by('-total_score', '-problems_solved',
                                                                               'last_submission')
    paginator = Paginator(participants, 10)  # Har sahifada 10 ta ishtirokchi
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_participants = participants.count()
    online_participants = participants.filter(
        last_activity__gte=timezone.now() - timezone.timedelta(seconds=300)).count()

    return render(request, 'contest/leaderboard.html', {
        'contest': contest,
        'page_obj': page_obj,
        'total_participants': total_participants,
        'online_participants': online_participants,
    })