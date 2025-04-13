
from portfolio.views import portfolio_view  # `your_app` ni loyihangizdagi app nomi bilan almashtiring

urlpatterns = [
    path('haqida/', portfolio_view, name='haqimda'),

]