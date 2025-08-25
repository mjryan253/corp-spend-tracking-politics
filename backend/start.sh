#!/bin/bash

echo "Starting Corporate Spending Tracker Backend..."

# Wait for database to be ready
echo "Waiting for database connection..."
python manage.py wait_for_db

# Check if database connection is successful
if python manage.py check --database default 2>/dev/null; then
    echo "Database connection successful!"
    
    # Run migrations
    echo "Running database migrations..."
    python manage.py migrate
    
    # Create superuser if it doesn't exist
    echo "Creating superuser if not exists..."
    python manage.py create_superuser_if_not_exists
    
    # Collect static files
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
else
    echo "Warning: Database connection failed. Skipping database operations."
    echo "The application will start but may not function properly without database access."
fi

# Start the Django development server
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000
