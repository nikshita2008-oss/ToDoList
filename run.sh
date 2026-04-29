#!/bin/bash

echo "Starting To-Do List Application..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if needed
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Initialize database if needed
if [ ! -f "todolist.db" ]; then
    echo "Initializing database..."
    python init_db.py
fi

# Start the application
echo ""
echo "========================================"
echo "To-Do List Application"
echo "========================================"
echo ""
echo "Starting server on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
