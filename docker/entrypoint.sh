#!/bin/sh

set -e #if any command fails, exit immediately

echo "Running database migrations..."
flask db upgrade

echo "Starting application..."
exec gunicorn --bind 0.0.0.0:5000 run:app