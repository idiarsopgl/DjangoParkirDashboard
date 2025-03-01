from django.core.management.base import BaseCommand
from django.conf import settings
from django.core import management
import os
import json
import shutil
import datetime
import sqlite3
from pathlib import Path

class Command(BaseCommand):
    help = 'Backup or restore the database and media files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            required=True,
            choices=['backup', 'restore'],
            help='Action to perform: backup or restore'
        )
        parser.add_argument(
            '--backup-path',
            type=str,
            help='Path for backup file or directory'
        )

    def handle(self, *args, **kwargs):
        action = kwargs['action']
        backup_path = kwargs.get('backup_path')

        if action == 'backup':
            self.perform_backup(backup_path)
        else:
            self.perform_restore(backup_path)

    def perform_backup(self, backup_path=None):
        # Create backup directory if it doesn't exist
        if not backup_path:
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'backup_{timestamp}')
        
        os.makedirs(backup_path, exist_ok=True)

        # Backup database
        db_file = settings.DATABASES['default']['NAME']
        backup_db = os.path.join(backup_path, 'db.sqlite3')
        
        # Create a copy of the database
        shutil.copy2(db_file, backup_db)

        # Backup media files if they exist
        media_dir = os.path.join(settings.BASE_DIR, 'media')
        if os.path.exists(media_dir):
            backup_media = os.path.join(backup_path, 'media')
            if os.path.exists(backup_media):
                shutil.rmtree(backup_media)
            shutil.copytree(media_dir, backup_media)

        # Create metadata file
        metadata = {
            'timestamp': datetime.datetime.now().isoformat(),
            'django_version': settings.DJANGO_VERSION,
            'backup_type': 'full',
        }
        
        with open(os.path.join(backup_path, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created backup at {backup_path}')
        )

    def perform_restore(self, backup_path):
        if not backup_path or not os.path.exists(backup_path):
            raise CommandError('Invalid backup path')

        # Verify backup metadata
        metadata_file = os.path.join(backup_path, 'metadata.json')
        if not os.path.exists(metadata_file):
            raise CommandError('Invalid backup: metadata.json not found')

        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        # Close all database connections
        db_file = settings.DATABASES['default']['NAME']
        
        # Restore database
        backup_db = os.path.join(backup_path, 'db.sqlite3')
        if os.path.exists(backup_db):
            # Create a backup of current database
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            shutil.copy2(db_file, f"{db_file}.{timestamp}.bak")
            
            # Replace current database with backup
            shutil.copy2(backup_db, db_file)

        # Restore media files
        backup_media = os.path.join(backup_path, 'media')
        if os.path.exists(backup_media):
            media_dir = os.path.join(settings.BASE_DIR, 'media')
            if os.path.exists(media_dir):
                shutil.rmtree(media_dir)
            shutil.copytree(backup_media, media_dir)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully restored from backup at {backup_path}')
        )
