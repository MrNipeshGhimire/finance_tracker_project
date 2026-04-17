#!/usr/bin/env bash

# Exit immediately if anything fails
set -o errexit

# Install all Python packages
pip install -r requirements.txt

# Collect static files (CSS, JS, images)
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate