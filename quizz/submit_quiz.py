from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
import json
import re
from .models import Quiz, Question, Choice, QuizSubmission, Answer, QuizSettings, Leaderboard, Badge

@login_required(login_url='ln')
@csrf_exempt
def submit_quiz(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Faqat POST so‘rovlar qabul qilinadi'}, status=400)

    try:
        data = json.loads(request.body)
        quiz_id = data.get('quiz_id')
        answers = data.get('answers')  # List: [{question_id, choice_id, text}]
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Noto‘g‘ri JSON formati'}, status=400)

    quiz = get_object_or_404(Quiz, id=quiz_id)
    if not quiz.is_ongoing:
        return JsonResponse({'error': 'Quiz yakunlangan yoki faol emas'}, status=403)

    # Urinishlarni tekshirish
    user_attempts = QuizSubmission.objects.filter(quiz=quiz, user=request.user).count()
    if user_attempts >= quiz.max_attempts:
        return JsonResponse({'error': 'Urinishlar soni chegarasidan oshdi'}, status=403)

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

        for answer_data in answers:
            question_id = answer_data.get('question_id')
            choice_id = answer_data.get('choice_id')
            text_answer = answer_data.get('text')

            # Savol quiz’ga tegishli ekanligini tekshirish
            question = get_object_or_404(Question, id=question_id, quiz=quiz)
            answer = Answer.objects.create(
                submission=submission,
                question=question,
                text_answer=text_answer
            )

            is_correct = False
            score = 0

            if question.question_type == 'MC':
                if choice_id:
                    choice = get_object_or_404(Choice, id=choice_id, question=question)
                    answer.selected_choice = choice
                    is_correct = choice.is_correct
            elif question.question_type == 'SA':
                # Qisqa javob uchun kalit so‘zlar bilan tekshirish
                correct_answer = question.choices.filter(is_correct=True).first()
                if correct_answer:
                    # Oddiy moslik o‘rniga regex yoki qisman moslik
                    pattern = re.compile(rf'\b{re.escape(correct_answer.text.lower())}\b', re.IGNORECASE)
                    is_correct = bool(pattern.search(text_answer.lower())) if text_answer else False
            elif question.question_type == 'CD':
                # Kod yozish uchun oddiy tekshirish (haqiqiy loyihada test case’lar kerak)
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
        if submission.total_score > 0:  # Faqat muvaffaqiyatli natijalarni qo‘shish
            leaderboard.entries.add(submission)

        # Badge berish logikasi
        user_quizzes = QuizSubmission.objects.filter(user=request.user, is_completed=True)
        high_score_count = user_quizzes.filter(stars__gte=3).count()
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
            'leaderboard_position': leaderboard_position,
            'message': 'Tabriklar, quiz muvaffaqiyatli yakunlandi!' if stars >= 3 else 'Yaxshi urinish, keyingi safar ko‘proq yulduz oling!'
        }

        # Agar yuqori ball bo‘lsa, confetti effekti
        if percentage >= 90:
            response_data['confetti'] = True

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Xatolik yuz berdi'}, status=500)