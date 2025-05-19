#!/bin/bash

# Stop any running gunicorn processes
echo "Stopping any running gunicorn processes..."
pkill -f gunicorn || true

# Install or update required packages
echo "Installing required packages..."
pip install -r requirements.txt

# Initialize the database (if needed)
echo "Initializing the database..."
python init-db.py

# Start the application with gunicorn
echo "Starting the application with gunicorn..."
gunicorn -c gunicorn_config.py run:app &

echo "Server started! Access at: http://localhost:10000"
