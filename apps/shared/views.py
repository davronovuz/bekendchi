from django.shortcuts import render
from .models import Banner
import random


def home_page(request):
    banners = Banner.objects.filter(is_active=True)
    random_banner = random.choice(banners) if banners.exists() else None
    return render(request, 'home.html', {'banner': random_banner})
