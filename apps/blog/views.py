from django.views.generic import ListView, DetailView
from .models import BlogPost, Category
from taggit.models import Tag
from django.core.paginator import Paginator

class BlogListView(ListView):
    model = BlogPost
    template_name = 'blog.html'
    context_object_name = 'posts'
    paginate_by = 6  # Har bir sahifada 6 ta maqola

    def get_queryset(self):
        return BlogPost.objects.filter(status='published').order_by('-first_published_at')

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'blog_detail.html'
    context_object_name = 'post'

    def get_object(self):
        obj = super().get_object()
        obj.views += 1  # Ko‘rishlar sonini oshirish
        obj.save()
        return obj

class CategoryDetailView(ListView):
    model = BlogPost
    template_name = 'category_detail.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        return BlogPost.objects.filter(category__slug=self.kwargs['slug'], status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(slug=self.kwargs['slug'])
        return context

class TagDetailView(ListView):
    model = BlogPost
    template_name = 'tag_detail.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        return BlogPost.objects.filter(tags__slug=self.kwargs['slug'], status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = Tag.objects.get(slug=self.kwargs['slug'])
        return context