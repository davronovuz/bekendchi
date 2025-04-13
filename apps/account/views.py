from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views import View
from .forms import CustomUserCreationForm  # Quyida yaratiladi
from .models import User







def custom_404(request, exception=None):
    return render(request, '404.html', status=404)



class SignupView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'authorization/signup.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Ro‘yxatdan muvaffaqiyatli o‘tdingiz!")
            return redirect('home')  # Bosh sahifaga yo‘naltirish
        return render(request, 'authorization/signup.html', {'form': form})

class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'authorization/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Xush kelibsiz, {username}!")
                return redirect('home')  # Bosh sahifaga yo‘naltirish
        messages.error(request, "Noto‘g‘ri foydalanuvchi nomi yoki parol.")
        return render(request, 'authorization/login.html', {'form': form})

class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "Tizimdan muvaffaqiyatli chiqdingiz!")
        return render(request, 'authorization/logout.html')




class Custom404Middleware:
    """
    Middleware to handle 404 errors and redirect to a custom 404.html page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if the response status code is 404
        if response.status_code == 404:
            return render(request, '404.html', status=404)
        
        return response