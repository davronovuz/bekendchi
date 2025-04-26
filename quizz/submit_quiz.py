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
        answers = data.get('answers', [])
        print("Received answers:", answers)  # Log qo‘shish
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Noto‘g‘ri JSON formati'}, status=400)

    quiz = get_object_or_404(Quiz, id=quiz_id)
    if not quiz.is_ongoing:
        return JsonResponse({'error': 'Quiz yakunlangan yoki faol emas'}, status=403)

    user_attempts = QuizSubmission.objects.filter(quiz=quiz, user=request.user).count()
    if user_attempts >= quiz.max_attempts:
        return JsonResponse({'error': 'Urinishlar soni chegarasidan oshdi'}, status=403)

    # Agar answers ro‘yxati bo‘sh bo‘lsa, xato qaytarish
    if not answers:
        return JsonResponse({'error': 'Hech qanday javob yuborilmadi. Iltimos, kamida bitta savolga javob bering.'}, status=400)

    settings = QuizSettings.objects.first() or QuizSettings()
    points_per_correct = settings.points_per_correct if settings.points_per_correct > 0 else 1
    streak_bonus = settings.streak_bonus if settings.streak_bonus >= 0 else 0
    max_streak = settings.max_streak if settings.max_streak > 0 else 5

    with transaction.atomic():
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
        detailed_results = []

        question_ids = [answer_data.get('question_id') for answer_data in answers if answer_data.get('question_id')]
        questions = Question.objects.filter(id__in=question_ids, quiz=quiz).in_bulk()

        for answer_data in answers:
            question_id = answer_data.get('question_id')
            choice_id = answer_data.get('choice_id')
            text_answer = answer_data.get('text', '').strip() if answer_data.get('text') is not None else None

            if not question_id or question_id not in questions:
                print(f"Question ID {question_id} not found or invalid.")
                continue

            question = questions[question_id]
            selected_choice = None
            if question.question_type == 'MC' and choice_id:
                try:
                    selected_choice = Choice.objects.get(id=choice_id, question=question)
                    print(f"Selected choice for question {question_id}: {selected_choice.text}")
                except Choice.DoesNotExist:
                    print(f"Choice ID {choice_id} not found for question {question_id}")
                    selected_choice = None
            else:
                print(f"No choice_id provided for MC question {question_id}")

            # `text_answer` ni aniq saqlash
            if question.question_type in ['SA', 'CD'] and text_answer is None:
                print(f"No text answer provided for {question.question_type} question {question_id}")
                text_answer = None

            # `Answer` ob'ektini yaratish
            answer = Answer.objects.create(
                submission=submission,
                question=question,
                selected_choice=selected_choice,
                text_answer=text_answer
            )

            # Saqlangan qiymatlarni tekshirish
            saved_answer = Answer.objects.get(id=answer.id)
            print(f"Answer saved for question {question_id}: selected_choice={saved_answer.selected_choice}, text_answer={saved_answer.text_answer}")

            is_correct = False
            score = 0
            result_detail = {
                'question_id': question_id,
                'question_text': question.text[:50],
                'type': question.question_type,
                'user_answer': None,
                'correct_answer': None,
                'is_correct': False,
                'score': 0,
                'saved': True
            }

            if question.question_type == 'MC':
                if selected_choice:
                    is_correct = selected_choice.is_correct
                    result_detail['user_answer'] = selected_choice.text
                    correct_answer = question.choices.filter(is_correct=True).first()
                    result_detail['correct_answer'] = correct_answer.text if correct_answer else "N/A"
                else:
                    result_detail['user_answer'] = "Javob tanlanmagan"
                    result_detail['correct_answer'] = question.choices.filter(is_correct=True).first().text if question.choices.filter(is_correct=True).exists() else "N/A"
                    result_detail['saved'] = False
            elif question.question_type == 'SA':
                if text_answer:
                    correct_answer = question.choices.filter(is_correct=True).first()
                    if correct_answer:
                        is_correct = text_answer.lower().strip() == correct_answer.text.lower().strip()
                        result_detail['user_answer'] = text_answer
                        result_detail['correct_answer'] = correct_answer.text
                else:
                    result_detail['user_answer'] = "Javob kiritilmagan"
                    result_detail['correct_answer'] = question.choices.filter(is_correct=True).first().text if question.choices.filter(is_correct=True).exists() else "N/A"
                    result_detail['saved'] = False
            elif question.question_type == 'CD':
                if text_answer:
                    correct_answer = question.choices.filter(is_correct=True).first()
                    if correct_answer:
                        is_correct = text_answer.strip() == correct_answer.text.strip()
                        result_detail['user_answer'] = text_answer
                        result_detail['correct_answer'] = correct_answer.text
                else:
                    result_detail['user_answer'] = "Javob kiritilmagan"
                    result_detail['correct_answer'] = question.choices.filter(is_correct=True).first().text if question.choices.filter(is_correct=True).exists() else "N/A"
                    result_detail['saved'] = False

            if is_correct:
                score = question.points * points_per_correct
                correct_answers += 1
                current_streak += 1
                if current_streak <= max_streak:
                    score += streak_bonus
                    streak = max(streak, current_streak)
                print(f"Question {question_id} correct! Score: {score}")
            else:
                wrong_answers += 1
                current_streak = 0
                print(f"Question {question_id} incorrect! Score: {score}")

            answer.is_correct = is_correct
            answer.score = score
            answer.save()
            total_score += score

            result_detail['is_correct'] = is_correct
            result_detail['score'] = score
            detailed_results.append(result_detail)

        total_questions = quiz.questions.count()
        unanswered = total_questions - (correct_answers + wrong_answers)
        wrong_answers += unanswered

        percentage = (correct_answers / max(1, total_questions)) * 100
        star_thresholds = settings.star_thresholds or {'1': 0, '2': 60, '3': 80}
        stars = 3 if percentage >= star_thresholds.get('3', 80) else \
                2 if percentage >= star_thresholds.get('2', 60) else \
                1 if percentage >= star_thresholds.get('1', 0) else 0

        submission.total_score = total_score
        submission.correct_answers = correct_answers
        submission.wrong_answers = wrong_answers
        submission.streak = streak
        submission.stars = stars
        submission.is_completed = True
        submission.save()

        leaderboard, _ = Leaderboard.objects.get_or_create(quiz=quiz)
        if submission.total_score > 0:
            leaderboard.entries.add(submission)

        user_quizzes = QuizSubmission.objects.filter(user=request.user, is_completed=True)
        high_score_count = user_quizzes.filter(stars__gte=3).count()
        if high_score_count >= 5:
            badge, _ = Badge.objects.get_or_create(
                name="Quiz Chempioni",
                defaults={'icon': '🏆', 'description': '5 ta quiz’da 3 yulduz olgan!'}
            )
            badge.users.add(request.user)

        leaderboard_position = leaderboard.entries.filter(total_score__gt=total_score).count() + 1

        response_data = {
            'status': 'success',
            'total_score': total_score,
            'correct_answers': correct_answers,
            'wrong_answers': wrong_answers,
            'unanswered': unanswered,
            'total_questions': total_questions,
            'streak': streak,
            'stars': stars,
            'leaderboard_position': leaderboard_position,
            'message': 'Tabriklar, quiz muvaffaqiyatli yakunlandi!' if stars >= 3 else 'Yaxshi urinish, keyingi safar ko‘proq yulduz oling!',
            'detailed_results': detailed_results
        }

        if percentage >= 90:
            response_data['confetti'] = True

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Xatolik yuz berdi'}, status=500)