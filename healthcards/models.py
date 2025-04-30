from django.db import models
from django.conf import settings
from accounts.models import Team

class HealthCard(models.Model):
    """
    Health card model
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Session(models.Model):
    """
    Session model - for each health check session
    """
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Vote(models.Model):
    """
    Vote model - votes given by users to health cards
    """
    RED = 'red'
    AMBER = 'amber'
    GREEN = 'green'
    
    STATUS_CHOICES = [
        (RED, 'Red'),
        (AMBER, 'Amber'),
        (GREEN, 'Green'),
    ]
    
    TREND_CHOICES = [
        ('better', 'Getting Better'),
        ('same', 'Same'),
        ('worse', 'Getting Worse'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_votes')
    health_card = models.ForeignKey(HealthCard, on_delete=models.CASCADE, related_name='card_votes')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='session_votes')
    status = models.CharField(max_length=5, choices=STATUS_CHOICES)
    trend = models.CharField(max_length=10, choices=TREND_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # A user can only give one vote for a card in a session for a team
        unique_together = ('user', 'team', 'health_card', 'session')
    
    def __str__(self):
        return f"{self.user.username} - {self.health_card.name} - {self.status}"

class TeamSummary(models.Model):
    """
    Team summary model - summary of teams' performance on health cards
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='summaries')
    health_card = models.ForeignKey(HealthCard, on_delete=models.CASCADE, related_name='card_summaries')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='session_summaries')
    
    red_count = models.IntegerField(default=0)
    amber_count = models.IntegerField(default=0)
    green_count = models.IntegerField(default=0)
    
    better_count = models.IntegerField(default=0)
    same_count = models.IntegerField(default=0)
    worse_count = models.IntegerField(default=0)
    
    total_votes = models.IntegerField(default=0)
    
    red_percentage = models.FloatField(default=0)
    amber_percentage = models.FloatField(default=0)
    green_percentage = models.FloatField(default=0)
    
    better_percentage = models.FloatField(default=0)
    same_percentage = models.FloatField(default=0)
    worse_percentage = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('team', 'health_card', 'session')
    
    def __str__(self):
        return f"{self.team.name} - {self.health_card.name} - {self.session.name}"
    
    def calculate_summary(self):
        """Calculates the summary based on team members' votes"""
        votes = Vote.objects.filter(
            team=self.team,
            health_card=self.health_card,
            session=self.session
        )
        
        # Count votes by status
        self.red_count = votes.filter(status=Vote.RED).count()
        self.amber_count = votes.filter(status=Vote.AMBER).count()
        self.green_count = votes.filter(status=Vote.GREEN).count()
        
        # Count votes by trend
        self.better_count = votes.filter(trend='better').count()
        self.same_count = votes.filter(trend='same').count()
        self.worse_count = votes.filter(trend='worse').count()
        
        # Calculate percentages and set total_votes
        total_votes = votes.count()
        self.total_votes = total_votes
        
        if total_votes > 0:
            self.red_percentage = (self.red_count / total_votes) * 100
            self.amber_percentage = (self.amber_count / total_votes) * 100
            self.green_percentage = (self.green_count / total_votes) * 100
            
            self.better_percentage = (self.better_count / total_votes) * 100
            self.same_percentage = (self.same_count / total_votes) * 100
            self.worse_percentage = (self.worse_count / total_votes) * 100
        else:
            self.red_percentage = self.amber_percentage = self.green_percentage = 0
            self.better_percentage = self.same_percentage = self.worse_percentage = 0
        
        self.save()
