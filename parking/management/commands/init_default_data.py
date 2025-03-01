from django.core.management.base import BaseCommand
from parking.models import ParkingRate, Language

class Command(BaseCommand):
    help = 'Initialize default parking rates and languages'

    def handle(self, *args, **kwargs):
        # Initialize default parking rates
        default_rates = [
            {
                'vehicle_type': 'CAR',
                'base_rate': 5000,  # Rp 5,000 per hour
                'grace_period_minutes': 15,
                'daily_max_rate': 50000,  # Rp 50,000 per day
            },
            {
                'vehicle_type': 'MOTORCYCLE',
                'base_rate': 2000,  # Rp 2,000 per hour
                'grace_period_minutes': 15,
                'daily_max_rate': 20000,  # Rp 20,000 per day
            },
            {
                'vehicle_type': 'TRUCK',
                'base_rate': 10000,  # Rp 10,000 per hour
                'grace_period_minutes': 15,
                'daily_max_rate': 100000,  # Rp 100,000 per day
            },
        ]

        for rate_data in default_rates:
            ParkingRate.objects.get_or_create(
                vehicle_type=rate_data['vehicle_type'],
                defaults={
                    'base_rate': rate_data['base_rate'],
                    'grace_period_minutes': rate_data['grace_period_minutes'],
                    'daily_max_rate': rate_data['daily_max_rate'],
                }
            )
            self.stdout.write(f"Created/Updated parking rate for {rate_data['vehicle_type']}")

        # Initialize languages
        languages = [
            {
                'code': 'en',
                'name': 'English',
                'is_default': True,
            },
            {
                'code': 'id',
                'name': 'Bahasa Indonesia',
                'is_default': False,
            },
        ]

        for lang_data in languages:
            Language.objects.get_or_create(
                code=lang_data['code'],
                defaults={
                    'name': lang_data['name'],
                    'is_default': lang_data['is_default'],
                }
            )
            self.stdout.write(f"Created/Updated language: {lang_data['name']}")

        self.stdout.write(self.style.SUCCESS('Successfully initialized default data'))
