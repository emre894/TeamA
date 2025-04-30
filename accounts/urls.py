from django.urls import path
from . import views
from healthcards.views import department_team_summaries  # Import the missing function

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('register/team-leader/', views.register_team_leader, name='register_team_leader'),
    path('register/senior-manager/', views.register_senior_manager, name='register_senior_manager'),
    path('register/department-leader/', views.register_department_leader, name='register_department_leader'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('team-leader-dashboard/', views.team_leader_dashboard, name='team_leader_dashboard'),
    path('senior-manager-dashboard/', views.senior_manager_dashboard, name='senior_manager_dashboard'),
    path('department-leader-dashboard/', views.department_leader_dashboard, name='department_leader_dashboard'),
    path('department-team-summaries/', department_team_summaries, name='department_team_summaries'),  # Now using the imported function
    path('profile/', views.profile_view, name='profile'),
    path('register/engineer/', views.register_engineer, name='register_engineer'),
    path('dashboard/', views.redirect_dashboard, name='dashboard'),
    path('dashboard/engineer/', views.engineer_dashboard, name='engineer_dashboard'),
    path('dashboard/team-leader/', views.team_leader_dashboard, name='team_leader_dashboard'),
    path('dashboard/senior-manager/', views.senior_manager_dashboard, name='senior_manager_dashboard'),
    path('', views.home, name='home'),
]