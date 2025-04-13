from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email manzilingiz'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Foydalanuvchi nomi'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Parolingizni kiriting'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Parolni qayta kiriting'})