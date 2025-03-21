# Generated by Django 5.0.1 on 2025-02-05 10:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0003_language_parkingrate'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BackupHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('MANUAL', 'Manual Backup'), ('AUTO', 'Automatic Backup'), ('RESTORE', 'Database Restore')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('file_size', models.BigIntegerField(help_text='Size in bytes')),
                ('status', models.CharField(default='Success', max_length=50)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Backup histories',
                'ordering': ['-created_at'],
            },
        ),
    ]
