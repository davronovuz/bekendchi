from django import forms
from .models import MidtermAssessment, MidtermTask, Student

class MidtermAssessmentForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        label="Talaba",
        widget=forms.Select(attrs={
            'class': 'midterm-form-select'
        })
    )
    assessment_number = forms.ChoiceField(
        choices=MidtermAssessment._meta.get_field('assessment_number').choices,
        label="Nazorat raqami",
        widget=forms.Select(attrs={
            'class': 'midterm-form-select'
        })
    )
    date = forms.DateField(
        label="Sana",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'midterm-form-input'
        })
    )
    comment = forms.CharField(
        required=False,
        label="Izoh",
        widget=forms.TextInput(attrs={
            'class': 'midterm-form-input',
            'placeholder': 'Nazorat ishi bo\'yicha umumiy izoh...'
        })
    )

    class Meta:
        model = MidtermAssessment
        fields = ['student', 'assessment_number', 'date', 'comment']


class MidtermTaskForm(forms.ModelForm):
    task_type = forms.CharField(
        label="Vazifa turi",
        widget=forms.TextInput(attrs={
            'class': 'midterm-form-input',
            'placeholder': 'Masalan: Test, Word amaliyoti, Excel amaliyoti'
        })
    )
    max_score = forms.FloatField(
        label="Maksimal ball",
        widget=forms.NumberInput(attrs={
            'class': 'midterm-form-input',
            'min': '0',
            'step': '0.1',
            'placeholder': 'Masalan: 10'
        })
    )
    score = forms.FloatField(
        label="Olgan ball",
        widget=forms.NumberInput(attrs={
            'class': 'midterm-form-input',
            'min': '0',
            'step': '0.1',
            'placeholder': 'Masalan: 8'
        })
    )
    comment = forms.CharField(
        required=False,
        label="Vazifa izohi",
        widget=forms.TextInput(attrs={
            'class': 'midterm-form-input',
            'placeholder': 'Izoh (ixtiyoriy)'
        })
    )

    class Meta:
        model = MidtermTask
        fields = ['task_type', 'max_score', 'score', 'comment']