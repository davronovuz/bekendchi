"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.urls import path, include
from django.contrib import admin


handler404 = lambda request, exception: render(request, '404.html', status=404)

urlpatterns =[
    path('egasi/', admin.site.urls,),
    path('tinymce/', include('tinymce.urls')),
    path('', include('apps.shared.urls')),
    path('blog/', include('apps.blog.urls')),
    path('account/', include('apps.account.urls')),
    path('problems/', include('problems.urls')),
    path('ustozlar/', include('ustoz.urls')),
    path('portfel/', include('apps.portfolio.urls')),
    path('contest/', include('contest.urls')),
    path('quiz/', include('quizz.urls')),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)