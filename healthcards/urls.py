from django.urls import path, include
from . import views
from django.http import HttpResponse

app_name = 'healthcards'  # This is important for URL namespacing

urlpatterns = [
    path('', views.teamhealth_index, name='teamhealth_index'),
    path('select-session/', views.select_session, name='select_session'),
    path('select-team/<int:session_id>/', views.select_team, name='select_team'),
    path('vote-cards/<int:session_id>/<int:team_id>/', views.vote_cards, name='vote_cards'),
    path('team-summary/<int:session_id>/<int:team_id>/', views.team_summary, name='team_summary'),
    path('card-progress/<int:card_id>/', views.card_progress, name='card_progress'),
    path('allteams/', views.all_teams, name='all_teams'),
    path('view-all-departments/', views.view_all_departments, name='view_all_departments'),
    path('senior_manager_team_summaries/', views.senior_team_summaries, name='senior_team_summaries'),
    path('my-votes/', views.my_votes, name='my_votes'),
]

