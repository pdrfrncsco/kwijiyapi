#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting deployment checks..."

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Creating staticfiles directory..."
mkdir -p /app/staticfiles

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
# Use PORT env var if set (Render/Heroku), otherwise default to 8000
PORT=${PORT:-8000}
echo "Starting Gunicorn on port $PORT..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3
