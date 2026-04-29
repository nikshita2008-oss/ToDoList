@echo off
echo Starting To-Do List Application...
echo.

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements if needed
echo Checking dependencies...
pip install -r requirements.txt > nul 2>&1

REM Initialize database if needed
if not exist "todolist.db" (
    echo Initializing database...
    python init_db.py
)

REM Start the application
echo.
echo ========================================
echo To-Do List Application
echo ========================================
echo.
echo Starting server on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
