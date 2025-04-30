from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Team,Department
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'is_team_leader', 'team', 'is_staff', 'is_active', 'user_type')
    list_filter = ('is_team_leader', 'team', 'is_staff', 'is_active', 'user_type')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_team_leader', 'groups', 'user_permissions')}),
        ('Team', {'fields': ('team',)}),
        ('User Type', {'fields': ('user_type',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active', 'is_team_leader', 'team', 'user_type')}
        ),
    )
    search_fields = ('email', 'username', 'user_type')
    ordering = ('email',)

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)



class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

admin.site.register(Department, DepartmentAdmin)



admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Team, TeamAdmin)
