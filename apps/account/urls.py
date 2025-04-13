from django.urls import path
from . import views

handler404 = views.custom_404  # Maxsus 404 handler

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='sn'),
    path('login/', views.LoginView.as_view(), name='ln'),
    path('logout/', views.LogoutView.as_view(), name='lt'),
]