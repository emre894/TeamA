from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import transaction  # Add this import at the top
from .models import HealthCard, Session, Vote, TeamSummary
from accounts.models import Team
from .forms import VoteForm, SessionSelectionForm, TeamSelectionForm, DateRangeForm, HealthCardSelectionForm
from accounts.models import *
from django.shortcuts import redirect

@login_required
def select_session(request):
    """
    Session selection page
    """
    if request.method == 'POST':
        form = SessionSelectionForm(request.POST)
        if form.is_valid():
            session = form.cleaned_data['session']
            return redirect('healthcards:select_team', session_id=session.id)
    else:
        form = SessionSelectionForm()
    
    return render(request, 'healthcards/select_session.html', {'form': form})

@login_required
def select_team(request, session_id):
    print("Logged-in user:", request.user.username)
    print("User type:", request.user.user_type)
    print("User team:", request.user.team)

    session = get_object_or_404(Session, id=session_id)

    if request.user.user_type == 'ENGINEER' and request.user.team:
        return redirect('healthcards:vote_cards', session_id=session.id, team_id=request.user.team.id)

    if request.user.user_type == 'DEPARTMENT_LEADER' and request.user.department:
        teams = Team.objects.filter(department=request.user.department)
    elif request.user.user_type == 'TEAM_LEADER' and request.user.team:
        teams = Team.objects.filter(id=request.user.team.id)
    elif request.user.user_type == 'SENIOR_MANAGER' or request.user.is_staff:
        teams = Team.objects.all()
    else:
        teams = Team.objects.none()

    if request.method == 'POST':
        form = TeamSelectionForm(request.POST)
        if form.is_valid():
            team = form.cleaned_data['team']
            return redirect('healthcards:vote_cards', session_id=session.id, team_id=team.id)
    else:
        form = TeamSelectionForm()

    return render(request, 'healthcards/select_team.html', {
        'form': form,
        'session': session,
        'teams': teams,
    })


@login_required
def vote_cards(request, session_id, team_id):
    """
    Health cards voting page
    """
    session = get_object_or_404(Session, id=session_id)
    team = get_object_or_404(Team, id=team_id)
    
    # Modified permission check to include department leaders and senior managers
    can_vote_for_team = False

    if request.user.user_type == 'ENGINEER':
        can_vote_for_team = request.user.team == team

    elif request.user.user_type == 'TEAM_LEADER':
        can_vote_for_team = request.user.team == team

    elif request.user.user_type == 'DEPARTMENT_LEADER':
        can_vote_for_team = request.user.department == team.department

    elif request.user.user_type == 'SENIOR_MANAGER' or request.user.is_staff:
        can_vote_for_team = True

    if not can_vote_for_team:
        messages.error(request, 'You cannot vote for this team.')
        return redirect('healthcards:select_session')
    
    health_cards = HealthCard.objects.all()
    
    # Get the user's previous votes
    user_votes = Vote.objects.filter(
        user=request.user,
        session=session,
        team=team
    ).select_related('health_card')
    
    # Convert user votes to a dictionary
    user_votes_dict = {vote.health_card.id: vote for vote in user_votes}
    
    if request.method == 'POST':
        health_card_id = request.POST.get('card_id')
        print(f"Received card_id: {health_card_id}")  
        
        try:
            health_card = HealthCard.objects.get(id=health_card_id)
            print(f"Found health card: {health_card.name}")
        except HealthCard.DoesNotExist:
            print(f"No health card found with id {health_card_id}")
            messages.error(request, f"Error: Health card with ID {health_card_id} not found.")
            return redirect('healthcards:vote_cards', session_id=session_id, team_id=team_id)
        
        # Check if the user has already voted for this card
        vote = user_votes_dict.get(int(health_card_id))
        
        # Create a copy of POST data that we can modify
        post_data = request.POST.copy()
        post_data['health_card'] = health_card_id  # Add health_card to the form data
        
        if vote:
            # Update existing vote
            form = VoteForm(post_data, instance=vote, user=request.user, team=team, session=session)
        else:
            # Create new vote
            form = VoteForm(post_data, user=request.user, team=team, session=session)
        
        # Add this debug code
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
            # Still try to save with the existing valid data
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
        
        # Try to save anyway
        try:
            with transaction.atomic():
                vote = form.save(commit=False)
                vote.user = request.user
                vote.team = team
                vote.session = session
                vote.health_card = health_card
                
                # Make sure status and trend values are valid
                if 'status' not in request.POST or not request.POST['status']:
                    vote.status = 'green'  # Default value
                if 'trend' not in request.POST or not request.POST['trend']:
                    vote.trend = 'same'    # Default value
                
                vote.save()
                
                print(f"Vote saved: status={vote.status}, trend={vote.trend}")
                
                # Update team summary inside the transaction
                update_team_summary(team, health_card, session)
                
                # Verify the vote was saved
                saved_votes = Vote.objects.filter(
                    user=request.user,
                    team=team,
                    health_card=health_card,
                    session=session
                )
                print(f"Verified saved votes count: {saved_votes.count()}")
                
                messages.success(request, f'Your vote for {health_card.name} has been recorded.')
        except Exception as e:
            print(f"Error saving vote: {e}")
            messages.error(request, f"Error saving vote: {e}")
    
    # This code will run whether or not we saved a vote
    # Create a form for each card
    card_forms = []
    for card in health_cards:
        # Get the latest vote data after potential save
        vote = Vote.objects.filter(
            user=request.user,
            team=team,
            health_card=card,
            session=session
        ).first()
        
        if vote:
            form = VoteForm(instance=vote, initial={'health_card': card})
        else:
            form = VoteForm(initial={'health_card': card})
        card_forms.append((card, form))
    
    return render(request, 'healthcards/vote_cards.html', {
        'session': session,
        'team': team,
        'card_forms': card_forms
    })

@login_required
def team_summary(request, session_id, team_id):
    """
    Team summary page
    """
    session = get_object_or_404(Session, id=session_id)
    team = get_object_or_404(Team, id=team_id)
    
    # First, load all votes directly to verify they exist
    all_votes = Vote.objects.filter(
        team=team,
        session=session
    )
    print(f"Found {all_votes.count()} total votes for team {team.name} in session {session.name}")
    for vote in all_votes:
        print(f"Vote: card={vote.health_card.name}, status={vote.status}, trend={vote.trend}")
    
    # Get team summaries
    summaries = TeamSummary.objects.filter(
        session=session,
        team=team
    ).select_related('health_card')
    
    # If no summaries exist, create them
    if not summaries.exists():
        print("No summaries exist, creating them now")
        for card in HealthCard.objects.all():
            summary, created = TeamSummary.objects.get_or_create(
                team=team,
                health_card=card,
                session=session
            )
            summary.calculate_summary()
    
    # Force recalculation and refresh the summaries from the database
    print("Forcing recalculation of all summaries")
    for card in HealthCard.objects.all():
        update_team_summary(team, card, session)
    
    # Reload the summaries to get the updated values
    summaries = TeamSummary.objects.filter(
        session=session,
        team=team
    ).select_related('health_card')
    
    # Print summaries to verify
    for summary in summaries:
        print(f"Summary for {summary.health_card.name}: red={summary.red_count}, amber={summary.amber_count}, green={summary.green_count}")
    
    # Calculate overall statistics for charts
    overall_red_count = sum(summary.red_count for summary in summaries)
    overall_amber_count = sum(summary.amber_count for summary in summaries)
    overall_green_count = sum(summary.green_count for summary in summaries)
    
    overall_better_count = sum(summary.better_count for summary in summaries)
    overall_same_count = sum(summary.same_count for summary in summaries)
    overall_worse_count = sum(summary.worse_count for summary in summaries)
    
    # Calculate overall percentages
    overall_total = overall_red_count + overall_amber_count + overall_green_count
    if overall_total > 0:
        overall_red_percentage = round((overall_red_count / overall_total) * 100)
        overall_amber_percentage = round((overall_amber_count / overall_total) * 100)
        overall_green_percentage = round((overall_green_count / overall_total) * 100)
        
        overall_better_percentage = round((overall_better_count / overall_total) * 100)
        overall_same_percentage = round((overall_same_count / overall_total) * 100)
        overall_worse_percentage = round((overall_worse_count / overall_total) * 100)
    else:
        overall_red_percentage = overall_amber_percentage = overall_green_percentage = 0
        overall_better_percentage = overall_same_percentage = overall_worse_percentage = 0
    
    # Add all the calculated values to the render context
    return render(request, 'healthcards/team_summary.html', {
        'session': session,
        'team': team,
        'team_summary': summaries,
        'summaries': summaries,
        'total_votes': all_votes.count(),
        # Add overall statistics
        'overall_red_count': overall_red_count,
        'overall_amber_count': overall_amber_count,
        'overall_green_count': overall_green_count,
        'overall_better_count': overall_better_count,
        'overall_same_count': overall_same_count,
        'overall_worse_count': overall_worse_count,
        'overall_red_percentage': overall_red_percentage,
        'overall_amber_percentage': overall_amber_percentage,
        'overall_green_percentage': overall_green_percentage,
        'overall_better_percentage': overall_better_percentage,
        'overall_same_percentage': overall_same_percentage,
        'overall_worse_percentage': overall_worse_percentage,
    })

@login_required
def card_progress(request, card_id=None):
    """
    Card progress page
    """
    # Use the card_id parameter here
    health_card = None
    if card_id:
        health_card = get_object_or_404(HealthCard, id=card_id)
    
    if not request.user.is_team_leader and not request.user.user_type == 'SENIOR_MANAGER':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        date_form = DateRangeForm(request.POST)
        card_form = HealthCardSelectionForm(request.POST)
        team_form = TeamSelectionForm(request.POST)
        
        if date_form.is_valid() and card_form.is_valid() and team_form.is_valid():
            start_date = date_form.cleaned_data['start_date']
            end_date = date_form.cleaned_data['end_date']
            health_card = card_form.cleaned_data['health_card']
            team = team_form.cleaned_data['team']
            
            # Get sessions within the selected date range
            sessions = Session.objects.filter(
                start_date__gte=start_date,
                end_date__lte=end_date
            ).order_by('start_date')
            
            # Get team summaries for each session
            progress_data = []
            for session in sessions:
                summary = TeamSummary.objects.filter(
                    session=session,
                    team=team,
                    health_card=health_card
                ).first()
                
                if summary:
                    progress_data.append({
                        'session': session.name,
                        'red': summary.red_count,
                        'amber': summary.amber_count,
                        'green': summary.green_count,
                        'better': summary.better_count,
                        'same': summary.same_count,
                        'worse': summary.worse_count
                    })
            
            return render(request, 'healthcards/card_progress.html', {
                'date_form': date_form,
                'card_form': card_form,
                'team_form': team_form,
                'progress_data': progress_data,
                'health_card': health_card,
                'team': team,
                'start_date': start_date,
                'end_date': end_date
            })
    else:
        date_form = DateRangeForm()
        card_form = HealthCardSelectionForm()
        team_form = TeamSelectionForm()
    
    return render(request, 'healthcards/card_progress.html', {
        'date_form': date_form,
        'card_form': card_form,
        'team_form': team_form
    })

def update_team_summary(team, health_card, session):
    """Update team summary after new votes"""
    summary, created = TeamSummary.objects.get_or_create(
        team=team,
        health_card=health_card,
        session=session
    )
    
    # Add debug print
    print(f"Updating summary for team: {team.name}, card: {health_card.name}")
    
    # Get all votes for this team, card and session
    votes = Vote.objects.filter(
        team=team,
        health_card=health_card,
        session=session
    )
    
    # Add debug print
    print(f"Found {votes.count()} votes")
    
    # Count votes by status
    summary.red_count = votes.filter(status='red').count()
    summary.amber_count = votes.filter(status='amber').count()
    summary.green_count = votes.filter(status='green').count()
    
    # Count votes by trend
    summary.better_count = votes.filter(trend='better').count()
    summary.same_count = votes.filter(trend='same').count()
    summary.worse_count = votes.filter(trend='worse').count()
    
    # Calculate percentages
    total_votes = votes.count()
    if total_votes > 0:
        summary.red_percentage = round((summary.red_count / total_votes) * 100)
        summary.amber_percentage = round((summary.amber_count / total_votes) * 100)
        summary.green_percentage = round((summary.green_count / total_votes) * 100)
        
        summary.better_percentage = round((summary.better_count / total_votes) * 100)
        summary.same_percentage = round((summary.same_count / total_votes) * 100)
        summary.worse_percentage = round((summary.worse_count / total_votes) * 100)
        
        # Add this line to set the total votes count
        summary.total_votes = total_votes
    
    summary.save()
    print(f"Summary updated: {summary.red_count}/{summary.amber_count}/{summary.green_count}")
    return summary

# Redirect to select_session page when accessing the teamhealth index
def teamhealth_index(request):
    return redirect('healthcards:select_session')

def all_teams(request):
    teams = Team.objects.all()
    return render(request, 'healthcards/all_teams.html', {'teams': teams})

def view_all_departments(request):
    departments = Department.objects.all()
    return render(request, 'healthcards/view_all_departments.html', {'departments': departments})

def senior_team_summaries(request):
    """
        Senior team summaries page
    """
    
    summaries = TeamSummary.objects.all()
    sessions = Session.objects.all()
    teams = Team.objects.all()
    
    # Filter summaries based on GET request parameters
    team_id = request.GET.get('team')
    session_id = request.GET.get('session')
    
    if team_id and session_id:
        summaries = summaries.filter(team_id=team_id, session_id=session_id)
    
    return render(request, 'healthcards/team-summary-senior-manager.html', {'summaries': summaries, 'sessions': sessions, 'teams': teams})

@login_required
def department_team_summaries(request):
    """
    Department team summaries page - accessible only to department leaders
    """
    if not request.user.user_type == 'DEPARTMENT_LEADER':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    department = request.user.department
    teams = Team.objects.filter(department=department)
    team_ids = teams.values_list('id', flat=True)
    
    summaries = TeamSummary.objects.filter(team_id__in=team_ids)
    sessions = Session.objects.all()
    
    # Filter summaries based on GET request parameters
    session_id = request.GET.get('session')
    
    if session_id:
        summaries = summaries.filter(session_id=session_id)
    
    return render(request, 'healthcards/department_team_summaries.html', {
        'summaries': summaries, 
        'sessions': sessions, 
        'teams': teams,
        'department': department
    })

@login_required
def my_votes(request):
    if request.user.user_type not in ['ENGINEER', 'TEAM_LEADER']:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('dashboard')

    votes = Vote.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'healthcards/my_votes.html', {'votes': votes})





