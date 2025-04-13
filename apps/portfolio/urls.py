
from .views import portfolio_view  # `your_app` ni loyihangizdagi app nomi bilan almashtiring
from django.urls import path


urlpatterns = [
    path('haqida/', portfolio_view, name='haqimda'),

]