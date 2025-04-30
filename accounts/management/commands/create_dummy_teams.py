from django.core.management.base import BaseCommand
from accounts.models import Team, Department, CustomUser

class Command(BaseCommand):
    help = 'Creates dummy teams for testing'

    def add_arguments(self, parser):
        parser.add_argument('department_name', type=str, help='Department name to create teams for')
        parser.add_argument('--count', type=int, default=4, help='Number of teams to create')

    def handle(self, *args, **kwargs):
        department_name = kwargs['department_name']
        count = kwargs['count']
        
        # Get or create the department
        department, created = Department.objects.get_or_create(name=department_name)
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created new department: {department_name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing department: {department_name}'))
        
        # Create teams with varied descriptions
        team_descriptions = [
            "Frontend development team focused on user experience",
            "Backend engineering team working on API development",
            "DevOps team managing CI/CD pipelines and infrastructure",
            "Quality assurance team ensuring software reliability",
            "Data science team building analytics solutions",
            "Mobile application development team",
            "Security engineering team",
            "UX/UI design team"
        ]
        
        # Create teams
        created_count = 0
        for i in range(1, count+1):
            name = f"Team {i}"
            description = team_descriptions[(i-1) % len(team_descriptions)]
            
            team, team_created = Team.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'department': department
                }
            )
            
            if team_created:
                created_count += 1
                self.stdout.write(f'Created team: {name}')
            else:
                # If team exists but doesn't have department, update it
                if not team.department:
                    team.department = department
                    team.save()
                    self.stdout.write(f'Updated existing team: {name} to department {department_name}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} teams for {department_name}'))