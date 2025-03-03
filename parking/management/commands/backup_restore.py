from django.core.management.base import BaseCommand
from django.conf import settings as django_settings
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
        backup_dir = os.path.join(django_settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        # Generate backup filename with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.zip'
        
        # Use provided path or create one in the backup directory
        if not backup_path:
            backup_path = os.path.join(backup_dir, backup_filename)
        
        # Get database file path (assuming SQLite)
        db_file = django_settings.DATABASES['default']['NAME']
        
        # Create temporary directory for backup files
        temp_dir = os.path.join(backup_dir, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Copy media files
        media_dir = os.path.join(django_settings.BASE_DIR, 'media')
        if os.path.exists(media_dir):
            shutil.copytree(media_dir, os.path.join(temp_dir, 'media'))
        
        # Export database data
        management.call_command('dumpdata', exclude=['contenttypes', 'auth.permission'], output=os.path.join(temp_dir, 'db.json'))
        
        # Create metadata file
        metadata = {
            'timestamp': timestamp,
            'django_version': django_settings.DJANGO_VERSION,
            'backup_format_version': '1.0'
        }
        
        with open(os.path.join(temp_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)

        # Zip the backup files
        shutil.make_archive(backup_path, 'zip', temp_dir)

        # Clean up temporary files
        shutil.rmtree(temp_dir)

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
        db_file = django_settings.DATABASES['default']['NAME']
        
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
            media_dir = os.path.join(django_settings.BASE_DIR, 'media')
            if os.path.exists(media_dir):
                shutil.rmtree(media_dir)
            shutil.copytree(backup_media, media_dir)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully restored from backup at {backup_path}')
        )
