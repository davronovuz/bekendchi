from django.urls import path
from .views import group_list, group_attendance, update_attendance

urlpatterns = [
    path('', group_list, name='group_list'),
    path('group/<int:group_id>/', group_attendance, name='group_attendance'),
    path('group/<int:group_id>/update/', update_attendance, name='update_attendance'),
]