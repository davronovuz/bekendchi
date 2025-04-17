from django import forms

from contest.models import Submission


class CodeSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['code']
        widgets = {
            'code': forms.Textarea(attrs={
                'rows': 10,
                'class': 'form-control',
                'placeholder': 'Kodingizni shu yerga yozing...',
            }),
        }