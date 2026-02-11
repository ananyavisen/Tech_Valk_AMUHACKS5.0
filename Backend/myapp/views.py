from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import QuestionnaireResponse
from django.contrib import messages
from django.contrib.auth import logout
from .models import DailyLog, Resource
from django.utils import timezone
from .models import DailyLog
import random


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def signup_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(username=username, password=password)
        login(request, user)

        return redirect('questionnaire')

    return render(request, 'signup.html')

def home(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.profile.questionnaire_completed:
                return redirect('dashboard')
            else:
                return redirect('questionnaire')

        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')

    return render(request, 'login.html')

def signup_view(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Basic validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        # Create user
        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)

        return redirect('questionnaire')

    return render(request, 'signup.html')


@login_required
def questionnaire(request):

    if request.user.profile.questionnaire_completed:
        return redirect('dashboard')

    if request.method == "POST":

        response = QuestionnaireResponse.objects.filter(
            user=request.user
        ).first()

        if not response:
            response = QuestionnaireResponse(user=request.user)

        response.school_language = request.POST.get('q1')
        response.stage_activity = request.POST.get('q2')
        response.teaching_pace = request.POST.get('q3')
        response.doubt_clearing = request.POST.get('q4')

        response.extempore_comfort = int(request.POST.get('q5', 3))
        response.public_speaking_confidence = int(request.POST.get('q6', 3))
        response.help_seeking_comfort = int(request.POST.get('q7', 3))
        response.group_discussion_confidence = int(request.POST.get('q8', 3))
        response.adaptability = int(request.POST.get('q9', 3))

        response.academic_pressure = request.POST.get('q10')
        response.course = request.POST.get('q11')
        response.specialisation = request.POST.get('q12')

        response.calculate_score()
        response.save()

        profile = request.user.profile
        profile.questionnaire_completed = True
        profile.save()

        return redirect('dashboard')

    return render(request, 'questionnaire.html')


@login_required
def complete_quest(request):
    if request.method == "POST":

        profile = request.user.profile

        profile.fuel_bonus += 1   # 🔥 reward
        profile.save()

    return redirect("dashboard")

@login_required
def skip_quest(request):
    return redirect("dashboard")

@login_required
def dashboard(request):

    response = QuestionnaireResponse.objects.filter(
        user=request.user
    ).first()
    
    # Get user course
    user_course = response.course

    # Filter resources properly
    videos = Resource.objects.filter(
        category__iexact="Video",
        course__iexact=user_course
    )

    notes = Resource.objects.filter(
        category__iexact="Notes",
        course__iexact=user_course
    )

    articles = Resource.objects.filter(
        category__iexact="Article",
        course__iexact=user_course
    )

    if not response:
        return redirect('questionnaire')

    score = response.total_score

    MIN_SCORE = 8
    MAX_SCORE = 34
    MIN_FUEL = 10
    MAX_FUEL = 85

    normalized_score = round(
        ((score - MIN_SCORE) / (MAX_SCORE - MIN_SCORE)) * 100
    )

    base_fuel = MIN_FUEL + round(
        ((score - MIN_SCORE) / (MAX_SCORE - MIN_SCORE)) 
        * (MAX_FUEL - MIN_FUEL)
    )
    bonus = request.user.profile.fuel_bonus

    fuel_percentage = base_fuel + bonus
    fuel_percentage = min(100, fuel_percentage)
    fuel_percentage = max(MIN_FUEL, fuel_percentage)
    fuel_percentage = min(100, fuel_percentage)


    if fuel_percentage < 45:
        fuel_band='low'
        encouragement = "🌱 Building your foundation!"
    elif fuel_percentage < 70:
        fuel_band='medium'
        encouragement = "🏹 Keep going!"
    else:
        fuel_band='high'
        encouragement = "🚀 You're ready to launch!"
    
    # 🔥 Get latest daily log
    latest_log = DailyLog.objects.filter(
        user=request.user
    ).order_by('-created_at').first()
    if latest_log and latest_log.moods:
        first_mood = latest_log.moods.split(" | ")[0]
        
    else:
       first_mood = None
    #Quest sync with mood and fuel
    if fuel_band == "low":

        if first_mood == "😵 Overwhelmed State":
            quest_pool = [
                {"title": "Complete One 10-Minute Task", "description": "No pressure. Just begin."},
                {"title": "Write 3 Small Wins", "description": "Focus on what’s working."},
            ]

        elif first_mood == "😎 Confident Aura":
            quest_pool = [
                {"title": "Speak Once Today", "description": "Channel your confidence."},
                {"title": "Share Your Opinion in Class", "description": "Use your momentum wisely."},
            ]

        else:
            quest_pool = [
                {"title": "Write Down One Fear", "description": "Clarity builds courage."},
                {"title": "Do One Small Brave Thing", "description": "Courage grows slowly."},
            ]


    elif fuel_band == "medium":

        if first_mood == "😎 Confident Aura":
            quest_pool = [
                {"title": "Attempt a Mock Interview", "description": "Push your boundaries."},
                {"title": "Apply to One Internship", "description": "Take a bold step."},
            ]
        else:
            quest_pool = [
                {"title": "Participate in Discussion", "description": "Step slightly outside comfort."},
                {"title": "Ask One Question Publicly", "description": "Engage actively."},
            ]


    else:  # high fuel

        if first_mood == "😎 Confident Aura":
            quest_pool = [
                {"title": "Lead a Small Group Discussion", "description": "Take initiative boldly."},
                {"title": "Mentor a Junior", "description": "Confidence multiplies when shared."},
            ]
        else:
            quest_pool = [
                {"title": "Apply to 2 Opportunities", "description": "Momentum is on your side."},
                {"title": "Record a Self-Introduction Video", "description": "Polish your presence."},
            ]


    # 🎲 Randomize here
    quest = random.choice(quest_pool)
    recent_logs = DailyLog.objects.filter(
    user=request.user
).order_by('-created_at')

    resources = Resource.objects.filter(course=user_course)

    return render(request, 'dashboard.html', {
        'normalized_score': normalized_score,
        'fuel_percentage': fuel_percentage,
        'encouragement': encouragement,
        'latest_log': latest_log,
        'recent_logs': recent_logs,
        'notes': notes,
        'videos': videos,
        'articles': articles,
        'quest': quest
    })

@login_required
def save_daily_log(request):
    if request.method == "POST":

        moods = request.POST.get("selected_moods")
        reflection = request.POST.get("reflection")

        if reflection:

            today = timezone.now().date()

            existing_log = DailyLog.objects.filter(
                user=request.user,
                created_at__date=today
            ).first()

            if existing_log:
                existing_log.moods = moods
                existing_log.reflection = reflection
                existing_log.save()
            else:
                DailyLog.objects.create(
                    user=request.user,
                    moods=moods,
                    reflection=reflection
                )

        return redirect("dashboard")
