from django.urls import path
from . import views

app_name = 'contest'

urlpatterns = [
    path('', views.contest_list, name='contest_list'),  # Contest ro‘yxati
    path('<int:contest_id>/', views.contest_detail, name='contest_detail'),  # Contest masalalari
    path('problem/<int:problem_id>/', views.problem_detail, name='problem_detail'),  # Masala va kod yuborish
    path('<int:contest_id>/leaderboard/', views.leaderboard, name='leaderboard'),  # Leaderboard
    path('submit-code/', views.submit_code, name='submit_code'),  # AJAX kod yuborish
]