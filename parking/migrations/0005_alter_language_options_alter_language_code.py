# Generated by Django 5.1.6 on 2025-03-01 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0004_backuphistory'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='language',
            options={'ordering': ['name'], 'verbose_name': 'Bahasa', 'verbose_name_plural': 'Bahasa'},
        ),
        migrations.AlterField(
            model_name='language',
            name='code',
            field=models.CharField(choices=[('id', 'Bahasa Indonesia'), ('en', 'English'), ('jw', 'Basa Jawa'), ('su', 'Basa Sunda')], max_length=2, unique=True),
        ),
    ]
