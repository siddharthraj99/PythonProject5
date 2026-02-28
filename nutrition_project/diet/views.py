from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from .models import Food, UserDiet


def home(request):
    if request.method == 'POST':

        # REGISTER
        if 'register' in request.POST:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                return render(request, 'home.html', {'error': 'Passwords do not match'})

            if User.objects.filter(username=username).exists():
                return render(request, 'home.html', {'error': 'Username already exists'})

            User.objects.create_user(username=username, email=email, password=password)
            return render(request, 'home.html', {'success': 'Account created successfully!'})

        # LOGIN
        if 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                return render(request, 'home.html', {'error': 'Invalid credentials'})

    return render(request, 'home.html')


@login_required
def dashboard(request):
    today = now().date()

    logs = UserDiet.objects.filter(user=request.user)

    total_calories = sum(log.food.calories * log.quantity for log in logs)
    total_protein = sum(log.food.protein * log.quantity for log in logs)
    total_carbs = sum(log.food.carbs * log.quantity for log in logs)
    total_fats = sum(log.food.fats * log.quantity for log in logs)

    recent_logs = logs.order_by('-id')[:5]

    alerts = []

    if total_calories < 1500:
        alerts.append("⚠️ Calories intake is low today")

    if total_protein < 50:
        alerts.append("⚠️ Protein intake is low today")

    context = {
        'total_calories': round(total_calories, 2),
        'total_protein': round(total_protein, 2),
        'total_carbs': round(total_carbs, 2),
        'total_fats': round(total_fats, 2),
        'recent_logs': recent_logs,
        'alerts': alerts,
        'today': today
    }

    return render(request, 'dashboard.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')