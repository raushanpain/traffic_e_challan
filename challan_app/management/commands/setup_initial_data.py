from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from challan_app.models import ViolationType, PoliceOfficer
from django.utils import timezone

class Command(BaseCommand):
    help = 'Set up initial data for the Smart E-Challan System'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superuser created: admin/admin123'))
        
        try:
            # Create default violation types
            violation_types = [
                {
                    'name': 'Over Speeding',
                    'description': 'Driving above the prescribed speed limit',
                    'fine_amount': 1000.00,
                    'penalty_points': 3
                },
                {
                    'name': 'Signal Jumping',
                    'description': 'Violating traffic signal rules',
                    'fine_amount': 500.00,
                    'penalty_points': 2
                },
                {
                    'name': 'No Helmet',
                    'description': 'Riding two-wheeler without helmet',
                    'fine_amount': 300.00,
                    'penalty_points': 1
                },
                {
                    'name': 'No Seat Belt',
                    'description': 'Driving four-wheeler without seat belt',
                    'fine_amount': 400.00,
                    'penalty_points': 1
                },
                {
                    'name': 'Wrong Parking',
                    'description': 'Parking vehicle in unauthorized area',
                    'fine_amount': 200.00,
                    'penalty_points': 1
                },
                {
                    'name': 'Drunk Driving',
                    'description': 'Driving under influence of alcohol',
                    'fine_amount': 2000.00,
                    'penalty_points': 5
                },
                {
                    'name': 'Mobile Phone Usage',
                    'description': 'Using mobile phone while driving',
                    'fine_amount': 500.00,
                    'penalty_points': 2
                },
                {
                    'name': 'Overloading',
                    'description': 'Carrying passengers beyond capacity',
                    'fine_amount': 800.00,
                    'penalty_points': 2
                }
            ]
            
            for violation_data in violation_types:
                violation_type, created = ViolationType.objects.get_or_create(
                    name=violation_data['name'],
                    defaults=violation_data
                )
                if created:
                    self.stdout.write(f'Created violation type: {violation_type.name}')
                else:
                    self.stdout.write(f'Violation type already exists: {violation_type.name}')
            
            # Create a default police officer
            if not PoliceOfficer.objects.exists():
                admin_user = User.objects.get(username='admin')
                officer = PoliceOfficer.objects.create(
                    user=admin_user,
                    badge_number='PO001',
                    rank='Inspector',
                    station='Central Traffic Police Station',
                    contact_number='9876543210',
                    is_active=True
                )
                self.stdout.write(f'Created police officer: {officer}')
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not create violation types and police officer: {str(e)}'))
            self.stdout.write('You can create these manually through the admin interface.')
        
        self.stdout.write(self.style.SUCCESS('Initial data setup completed successfully!'))
        self.stdout.write('You can now login with admin/admin123')
