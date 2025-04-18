from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q, Count,Avg,Max
import json
import re
from .models import Quiz, QuizSubmission, Question, Choice, Answer, Subject, QuizSettings, Leaderboard, Badge


@login_required(login_url='ln')
def quiz_list(request):
    """Barcha faol quizlarni ro‘yxat sifatida ko‘rsatish"""
    subjects = Subject.objects.all()
    quizzes = Quiz.objects.filter(is_active=True).select_related('subject').annotate(
        participant_count=Count('submissions', distinct=True)
    )

    # Filtrlash
    subject_id = request.GET.get('subject')
    difficulty = request.GET.get('difficulty')
    search_query = request.GET.get('q')

    if subject_id:
        try:
            subject = Subject.objects.get(id=subject_id)
            quizzes = quizzes.filter(subject=subject)
        except Subject.DoesNotExist:
            pass

    if difficulty in ['oson', 'orta', 'qiyin']:
        quizzes = quizzes.filter(difficulty=difficulty)

    if search_query:
        quizzes = quizzes.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

    # Tartiblash
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'popular':
        quizzes = quizzes.order_by('-participant_count', '-created_at')
    else:
        quizzes = quizzes.order_by('-created_at')

    # Pagination
    paginator = Paginator(quizzes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Foydalanuvchi ishtiroki
    user_quizzes = set(QuizSubmission.objects.filter(user=request.user).values_list('quiz_id', flat=True))

    return render(request, 'quiz/quiz_list.html', {
        'page_obj': page_obj,
        'subjects': subjects,
        'selected_subject': subject_id,
        'selected_difficulty': difficulty,
        'search_query': search_query,
        'sort_by': sort_by,
        'user_quizzes': user_quizzes,
    })


@login_required(login_url='ln')
def quiz_detail(request, quiz_id):
    """Quiz detallari va savollarini ko‘rsatish"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    settings = QuizSettings.objects.first() or QuizSettings()

    # Foydalanuvchining oldingi urinishlari
    user_submissions = QuizSubmission.objects.filter(
        quiz=quiz,
        user=request.user
    ).select_related('quiz').order_by('-attempt_number')

    # Eng yaxshi natija
    best_submission = user_submissions.order_by('-total_score', '-correct_answers').first()

    # Urinish imkoniyati
    can_attempt = user_submissions.count() < quiz.max_attempts and quiz.is_ongoing

    # Savollar va variantlar
    questions = quiz.questions.all().prefetch_related('choices')

    # Leaderboard’dagi o‘rin
    leaderboard = Leaderboard.objects.filter(quiz=quiz).first()
    leaderboard_position = None
    if leaderboard and best_submission:
        leaderboard_position = leaderboard.entries.filter(total_score__gt=best_submission.total_score).count() + 1



    return render(request, 'quiz/quiz_detail.html', {
        'quiz': quiz,
        'questions': questions,
        'can_attempt': can_attempt,
        'user_submissions': user_submissions,
        'best_submission': best_submission,
        'settings': settings,
        'leaderboard_position': leaderboard_position,

    })


@login_required(login_url='ln')
def quiz_leaderboard(request, quiz_id):
    """Leaderboard ko‘rsatish"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    leaderboard = Leaderboard.objects.filter(quiz=quiz).first()

    # Eng yaxshi natijalar
    submissions = leaderboard.entries.all().select_related('user') if leaderboard else QuizSubmission.objects.none()

    # Pagination
    paginator = Paginator(submissions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistika
    total_participants = submissions.count()
    avg_score = submissions.aggregate(avg_score=Avg('total_score'))['avg_score'] or 0
    max_streak = submissions.aggregate(max_streak=Max('streak'))['max_streak'] or 0

    # Foydalanuvchining o‘rni
    user_submission = submissions.filter(user=request.user).order_by('-total_score').first()
    user_position = None
    if user_submission:
        user_position = submissions.filter(total_score__gt=user_submission.total_score).count() + 1

    return render(request, 'quiz/leaderboard.html', {
        'quiz': quiz,
        'page_obj': page_obj,
        'total_participants': total_participants,
        'avg_score': round(avg_score, 1),
        'max_streak': max_streak,
        'user_position': user_position,
    })

@login_required(login_url='ln')
@csrf_exempt
def submit_quiz(request):
    """Quiz javoblarini yuborish"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Faqat POST so‘rovlari qabul qilinadi'}, status=405)

    try:
        data = json.loads(request.body)
        quiz_id = data.get('quiz_id')
        answers = data.get('answers')  # Format: [{question_id: int, choice_id: int, text: str}, ...]
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Noto‘g‘ri JSON format'}, status=400)

    if not quiz_id or not answers:
        return JsonResponse({'error': 'Quiz ID yoki javoblar kiritilmagan'}, status=400)

    quiz = get_object_or_404(Quiz, id=quiz_id)
    if not quiz.is_ongoing:
        return JsonResponse({'error': 'Quiz yakunlangan'}, status=403)

    # Urinishlar sonini tekshirish
    user_attempts = QuizSubmission.objects.filter(quiz=quiz, user=request.user).count()
    if user_attempts >= quiz.max_attempts:
        return JsonResponse({'error': 'Urinishlar soni chegarasi'}, status=403)

    # Sozlamalarni olish
    settings = QuizSettings.objects.first() or QuizSettings()

    with transaction.atomic():
        # Yangi submission yaratish
        submission = QuizSubmission.objects.create(
            user=request.user,
            quiz=quiz,
            attempt_number=user_attempts + 1
        )

        total_score = 0
        correct_answers = 0
        wrong_answers = 0
        streak = 0
        current_streak = 0

        # Savollarni bir so‘rovda olish
        question_ids = [answer_data.get('question_id') for answer_data in answers if answer_data.get('question_id')]
        questions = Question.objects.filter(id__in=question_ids, quiz=quiz).in_bulk()

        for answer_data in answers:
            question_id = answer_data.get('question_id')
            choice_id = answer_data.get('choice_id')
            text_answer = answer_data.get('text')

            if not question_id or question_id not in questions:
                continue

            question = questions[question_id]
            answer = Answer.objects.create(
                submission=submission,
                question=question,
                text_answer=text_answer
            )

            is_correct = False
            score = 0

            if question.question_type == 'MC' and choice_id:
                try:
                    choice = Choice.objects.get(id=choice_id, question=question)
                    answer.selected_choice = choice
                    is_correct = choice.is_correct
                except Choice.DoesNotExist:
                    is_correct = False
            elif question.question_type == 'SA' and text_answer:
                correct_answer = question.choices.filter(is_correct=True).first()
                if correct_answer:
                    pattern = re.compile(rf'\b{re.escape(correct_answer.text.lower())}\b', re.IGNORECASE)
                    is_correct = bool(pattern.search(text_answer.lower()))
            elif question.question_type == 'CD' and text_answer:
                correct_answer = question.choices.filter(is_correct=True).first()
                if correct_answer:
                    is_correct = text_answer.strip() == correct_answer.text.strip()

            if is_correct:
                score = question.points * settings.points_per_correct
                correct_answers += 1
                current_streak += 1
                if current_streak <= settings.max_streak:
                    score += settings.streak_bonus
                    streak = max(streak, current_streak)
            else:
                wrong_answers += 1
                current_streak = 0

            answer.is_correct = is_correct
            answer.score = score
            answer.save()
            total_score += score

        # Yulduzlar hisoblash
        percentage = (correct_answers / max(1, (correct_answers + wrong_answers))) * 100
        stars = 3 if percentage >= settings.star_thresholds.get('3', 80) else \
                2 if percentage >= settings.star_thresholds.get('2', 60) else \
                1 if percentage >= settings.star_thresholds.get('1', 0) else 0

        # Submission ni yangilash
        submission.total_score = total_score
        submission.correct_answers = correct_answers
        submission.wrong_answers = wrong_answers
        submission.streak = streak
        submission.stars = stars
        submission.is_completed = True
        submission.save()

        # Leaderboard ga qo‘shish
        leaderboard, _ = Leaderboard.objects.get_or_create(quiz=quiz)
        if total_score > 0:
            leaderboard.entries.add(submission)

        # Badge berish
        high_score_count = QuizSubmission.objects.filter(
            user=request.user, stars__gte=3, is_completed=True
        ).count()
        if high_score_count >= 5:
            badge, _ = Badge.objects.get_or_create(
                name="Quiz Chempioni",
                defaults={'icon': '🏆', 'description': '5 ta quiz’da 3 yulduz olgan!'}
            )
            badge.users.add(request.user)

        # Leaderboard’dagi o‘rin
        leaderboard_position = leaderboard.entries.filter(total_score__gt=total_score).count() + 1

        response_data = {
            'status': 'success',
            'total_score': total_score,
            'correct_answers': correct_answers,
            'wrong_answers': wrong_answers,
            'streak': streak,
            'stars': stars,
            'submission_id': submission.id,
            'leaderboard_position': leaderboard_position,
            'message': 'Tabriklar, quiz muvaffaqiyatli yakunlandi!' if stars >= 3 else 'Yaxshi urinish, keyingi safar ko‘proq yulduz oling!'
        }

        if percentage >= 90:
            response_data['confetti'] = True

        return JsonResponse(response_data, status=200)