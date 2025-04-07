from django.contrib import admin
from .models import BlogPage, Category, BlogPageTag, BlogIndexPage, Comment


admin.site.register(BlogPage)
admin.site.register(Category)
admin.site.register(BlogPageTag)
admin.site.register(BlogIndexPage)
admin.site.register(Comment)


