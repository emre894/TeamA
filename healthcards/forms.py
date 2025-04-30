from django import forms
from .models import Vote, Session, HealthCard
from accounts.models import Team

class VoteForm(forms.ModelForm):
    """
    Voting form
    """
    class Meta:
        model = Vote
        fields = ('health_card', 'status', 'trend', 'comment')
        widgets = {
            'health_card': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.RadioSelect(),
            'trend': forms.RadioSelect(),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.team = kwargs.pop('team', None)
        self.session = kwargs.pop('session', None)
        super().__init__(*args, **kwargs)
        
        if 'health_card' in self.fields and self.initial.get('health_card'):
            self.fields['health_card'].widget = forms.HiddenInput()

class SessionSelectionForm(forms.Form):
    """
    Session selection form
    """
    session = forms.ModelChoiceField(
        queryset=Session.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label=None
    )

class TeamSelectionForm(forms.Form):
    """
    Team selection form
    """
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label=None
    )

class DateRangeForm(forms.Form):
    """
    Date range selection form
    """
    start_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

class HealthCardSelectionForm(forms.Form):
    """
    Health card selection form
    """
    health_card = forms.ModelChoiceField(
        queryset=HealthCard.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label=None
    ) 