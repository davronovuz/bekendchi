from django.urls import path
from .views import group_list, group_attendance, update_attendance
from . import views
urlpatterns = [
    path('', group_list, name='group_list'),
    path('group/<int:group_id>/', group_attendance, name='group_attendance'),
    path('group/<int:group_id>/update/', update_attendance, name='update_attendance'),

    path('midterms/', views.midtermassessment_list, name='midtermassessment_list'),
    path('midterms/create/', views.midtermassessment_create, name='midterm_create'),
    path('midterms/<int:pk>/edit/', views.midtermassessment_edit, name='midterm_edit'),
    path('midterms/<int:pk>/delete/', views.midtermassessment_delete, name='midterm_delete'),
]