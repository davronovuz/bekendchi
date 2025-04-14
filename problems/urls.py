from django.urls import path, re_path
from .views import problem_list, problem_detail, submit_code

urlpatterns = [
    path('', problem_list, name='problem_list'),
    # UUID uchun moslashtirilgan URL pattern
    re_path(r'^(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', problem_detail, name='problem_detail'),
    re_path(r'^(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/submit/$', submit_code, name='submit_code'),
]