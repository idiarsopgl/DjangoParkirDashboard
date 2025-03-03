#!/bin/bash

# Activate virtual environment
source /var/www/parkir/a/myenv/bin/activate

# Set environment variables
export DJANGO_SETTINGS_MODULE=parking_system.settings
export PYTHONPATH=/var/www/parkir/a

# Collect static files
python manage.py collectstatic --noinput

# Apply any pending migrations
python manage.py migrate

# Start Gunicorn server
exec gunicorn parking_system.wsgi:application \
    --name parking_django \
    --workers 3 \
    --bind=127.0.0.1:8000 \
    --log-level=info \
    --log-file=/var/log/gunicorn/parking-gunicorn.log \
    --access-logfile=/var/log/gunicorn/parking-access.log \
    --error-logfile=/var/log/gunicorn/parking-error.log \
    --capture-output \
    --enable-stdio-inheritance \
    --daemon 