from django.urls import path
from . import views

urlpatterns = [
    path('maqolalar/', views.BlogListView.as_view(), name='blog_list'),
    path('maqola/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag_detail'),
]