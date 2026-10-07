#!/usr/bin/env bash
set -eu

python -m pip install -r requirements.txt

# Apply committed schema migrations and collect static assets.
python manage.py migrate --noinput
python manage.py import_locations
python manage.py collectstatic --noinput