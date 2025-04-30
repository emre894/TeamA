from django.contrib import admin
from .models import HealthCard, Session, Vote, TeamSummary

class HealthCardAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

class SessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active', 'start_date', 'end_date')

class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'health_card', 'session', 'status', 'trend', 'created_at')
    search_fields = ('user__username', 'team__name', 'health_card__name')
    list_filter = ('status', 'trend', 'session', 'team', 'health_card')

class TeamSummaryAdmin(admin.ModelAdmin):
    list_display = ('team', 'health_card', 'session', 'red_count', 'amber_count', 'green_count')
    search_fields = ('team__name', 'health_card__name', 'session__name')
    list_filter = ('team', 'health_card', 'session')
    readonly_fields = ('red_count', 'amber_count', 'green_count', 'better_count', 'same_count', 'worse_count')

admin.site.register(HealthCard, HealthCardAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(TeamSummary, TeamSummaryAdmin)
