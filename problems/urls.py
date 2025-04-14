from django.urls import path
from .views import problem_list, problem_detail, submit_code

urlpatterns = [
    path('', problem_list, name='problem_list'),
    path('<int:pk>/', problem_detail, name='problem_detail'),
    path('<int:pk>/submit/', submit_code, name='submit_code'),
]