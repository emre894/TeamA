from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Custom user manager class for the custom user model.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email address is required'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_team_leader', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)
    
class Department(models.Model):
    """
    Department model
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# Update Team model to link to Department
class Team(models.Model):
    """
    Team model
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    """
    Custom user model
    """
    # Add department leader type to choices
    USER_TYPE_CHOICES = (
        ('ENGINEER', 'Engineer'),
        ('TEAM_LEADER', 'Team Leader'),
        ('DEPARTMENT_LEADER', 'Department Leader'),
        ('SENIOR_MANAGER', 'Senior Manager'),
    )
    
    email = models.EmailField(_('email address'), unique=True)
    is_team_leader = models.BooleanField(default=False)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='ENGINEER')
    
    # Add department field to link department leaders to their departments
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='department_members')
