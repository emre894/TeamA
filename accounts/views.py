from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model, update_session_auth_hash  # Add this import
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, TeamLeaderRegistrationForm, CustomAuthenticationForm, UserProfileForm,SeniorManagerRegistrationForm, DepartmentLeaderRegistrationForm, EngineerRegistrationForm, UserProfileForm, PasswordChangeForm
from .models import *
from healthcards.models import Vote  # Add this import
from django.shortcuts import render

def home(request):
    """
    Home page
    """
    return render(request, 'accounts/home.html')

def register_user(request):
    """
    User registration
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form, 'user_type': 'engineer'})

def register_team_leader(request):
    """
    Team leader registration
    """
    if request.method == 'POST':
        form = TeamLeaderRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Team leader registration successful!')
            return redirect('team_leader_dashboard')
    else:
        form = TeamLeaderRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form, 'user_type': 'team_leader'})

def login_view(request):
    """
    Login page
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # First try direct authentication
        user = authenticate(request, username=username, password=password)
        
        # If that fails, try finding user by email
        if user is None:
            User = get_user_model()
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """
    Logout
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def dashboard(request):
    """
    User dashboard
    """
    # Add this to fetch recent votes
    recent_votes = Vote.objects.filter(user=request.user).order_by('-updated_at')[:5]
    
    if request.user.is_team_leader:
        return redirect('team_leader_dashboard')
    elif request.user.user_type == 'SENIOR_MANAGER':
        return redirect('senior_manager_dashboard')
    elif request.user.user_type == 'DEPARTMENT_LEADER':
        return redirect('department_leader_dashboard')
    
    # Add recent_votes to the context dictionary:
    return render(request, 'accounts/dashboard.html', {
        'recent_votes': recent_votes,
    })

@login_required
def team_leader_dashboard(request):
    """
    Team leader dashboard
    """
    if not request.user.is_team_leader:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    return render(request, 'accounts/team_leader_dashboard.html')

# @login_required
# def profile(request):
#     """
#     User profile
#     """
#     if request.method == 'POST':
#         form = UserProfileForm(request.POST, instance=request.user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Profile updated successfully!')
#             return redirect('profile')
#     else:
#         form = UserProfileForm(instance=request.user)
    
#     return render(request, 'accounts/profile.html', {'form': form})

# # path('register/senior-manager/', views.register_senior_manager, name='register_senior_manager'),

def register_senior_manager(request):
    if request.method == 'POST':
        form = SeniorManagerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Senior manager registered successfully!')
            return redirect('login')
    else:
        form = SeniorManagerRegistrationForm()
    
    return render(request, 'accounts/register_senior_manager.html', {'form': form})

def senior_manager_dashboard(request):
    teams = Team.objects.all()
    departments = Department.objects.all()
    return render(request,'accounts/senior_manager_dashboard.html', {'teams': teams, 'departments': departments})

def register_department_leader(request):
    """
    Department leader registration
    """
    if request.method == 'POST':
        form = DepartmentLeaderRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Department leader registration successful!')
            return redirect('department_leader_dashboard')
    else:
        form = DepartmentLeaderRegistrationForm()
    return render(request, 'accounts/register_department_leader.html', {'form': form})

@login_required
def department_leader_dashboard(request):
    """
    Department leader dashboard
    """
    if not request.user.user_type == 'DEPARTMENT_LEADER':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    department = request.user.department
    teams = Team.objects.filter(department=department)
    
    return render(request, 'accounts/department_leader_dashboard.html', {
        'department': department,
        'teams': teams
    })


def register_engineer(request):
    if request.method == 'POST':
        form = EngineerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Engineer registration successful!')
            return redirect('engineer_dashboard')  # Create this view if not done yet
    else:
        form = EngineerRegistrationForm()
    return render(request, 'accounts/register_engineer.html', {'form': form})

@login_required
def redirect_dashboard(request):
    user = request.user

    if user.user_type == 'ENGINEER':
        return redirect('engineer_dashboard')
    elif user.user_type == 'TEAM_LEADER':
        return redirect('team_leader_dashboard')
    elif user.user_type == 'DEPARTMENT_LEADER':
        return redirect('department_leader_dashboard')
    elif user.user_type == 'SENIOR_MANAGER':
        return redirect('senior_manager_dashboard')
    else:
        messages.error(request, "Unknown user type.")
        return redirect('login')
    
@login_required
def engineer_dashboard(request):
    if request.user.user_type != 'ENGINEER':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    return render(request, 'accounts/engineer_dashboard.html')

@login_required
def team_leader_dashboard(request):
    if request.user.user_type != 'TEAM_LEADER':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    return render(request, 'accounts/team_leader_dashboard.html')

@login_required
def senior_manager_dashboard(request):
    if request.user.user_type != 'SENIOR_MANAGER':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    return render(request, 'accounts/senior_manager_dashboard.html')

def home(request):
    return render(request, 'accounts/home.html')

def profile_view(request):
    user = request.user
    profile_form = UserProfileForm(instance=user)
    password_form = PasswordChangeForm()
    profile_form = UserProfileForm(request.POST, instance=request.user)


    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=user)
        password_form = PasswordChangeForm(request.POST)

        if profile_form.is_valid() and password_form.is_valid():
            profile_form.save()

            current_password = password_form.cleaned_data.get('current_password')
            if user.check_password(current_password):
                user.set_password(password_form.cleaned_data['new_password'])
                user.save()
                update_session_auth_hash(request, user)  # keep user logged in
                messages.success(request, "Profile and password updated successfully.")
            else:
                messages.error(request, "Current password is incorrect.")

    return render(request, 'accounts/profile.html', {
        'form': profile_form,
        'password_form': password_form
    })





