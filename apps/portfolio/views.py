from django.shortcuts import render




def portfolio_view(request):
    tech_stack = [
        "Python", "Django", "PostgreSQL", "Aiogram", "DRF", "FastAPI", 
        "Docker", "Nginx", "AWS", "Linux", "Git", "GitHub", "CI/CD", 
        "Kubernetes", "HTML", "CSS", "Bootstrap"
    ]
    return render(request, 'portfolio.html', {'tech_stack': tech_stack})