from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='login'),  
    path('signup/', views.signup_view, name='signup'),
    path('questionnaire/', views.questionnaire, name='questionnaire'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('save-daily-log/', views.save_daily_log, name='save_daily_log'),
    path("complete-quest/", views.complete_quest, name="complete_quest"),
    path("skip-quest/", views.skip_quest, name="skip_quest"),

]
