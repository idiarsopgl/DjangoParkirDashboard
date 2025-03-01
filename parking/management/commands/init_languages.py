from django.core.management.base import BaseCommand
from parking.models import Language

class Command(BaseCommand):
    help = 'Initialize default languages'

    def handle(self, *args, **kwargs):
        languages = [
            {'code': 'id', 'name': 'Bahasa Indonesia', 'is_default': True},
            {'code': 'en', 'name': 'English', 'is_default': False},
            {'code': 'jw', 'name': 'Basa Jawa', 'is_default': False},
            {'code': 'su', 'name': 'Basa Sunda', 'is_default': False},
        ]

        for lang in languages:
            Language.objects.get_or_create(
                code=lang['code'],
                defaults={
                    'name': lang['name'],
                    'is_default': lang['is_default']
                }
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully initialized languages'))
