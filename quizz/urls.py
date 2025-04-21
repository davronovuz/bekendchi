from django.urls import path
from . import views

app_name = 'quizz'

urlpatterns = [
    path('quiz/', views.quiz_list, name='quizl'),
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('<int:quiz_id>/leaderboard/', views.quiz_leaderboard, name='quiz_leaderboard'),
    path('submit/', views.submit_quiz, name='submit_quiz'),
    path('check-answer/', views.check_answer, name='check_answer'),
]