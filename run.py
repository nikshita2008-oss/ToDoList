#!/usr/bin/env python3
"""
To-Do List Application Launcher
This script handles virtual environment setup, dependencies, database initialization,
and starts the Flask application.
"""

import os
import sys
import subprocess
import platform

def run_command(command, shell=False):
    """Run a shell command and return True if successful."""
    try:
        subprocess.run(command, shell=shell, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        print(f"Error: Command not found. Make sure you have the required tools installed.")
        return False

def create_venv():
    """Create virtual environment if it doesn't exist."""
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        if not run_command([sys.executable, "-m", "venv", "venv"]):
            print("Error: Failed to create virtual environment")
            sys.exit(1)

def get_python_executable():
    """Get the Python executable path for the virtual environment."""
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", "python.exe")
    else:
        return os.path.join("venv", "bin", "python")

def get_pip_executable():
    """Get the pip executable path for the virtual environment."""
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", "pip.exe")
    else:
        return os.path.join("venv", "bin", "pip")

def install_dependencies():
    """Install required packages from requirements.txt."""
    print("Checking dependencies...")
    pip_exec = get_pip_executable()
    
    if not os.path.exists("requirements.txt"):
        print("Error: requirements.txt not found")
        sys.exit(1)
    
    if not run_command([pip_exec, "install", "-q", "-r", "requirements.txt"]):
        print("Warning: Some dependencies may not have installed correctly")
        # Continue anyway as some might have succeeded

def initialize_database():
    """Initialize database if it doesn't exist."""
    if not os.path.exists("todolist.db"):
        print("Initializing database...")
        python_exec = get_python_executable()
        
        if not os.path.exists("init_db.py"):
            print("Error: init_db.py not found")
            sys.exit(1)
        
        if not run_command([python_exec, "init_db.py"]):
            print("Error: Failed to initialize database")
            sys.exit(1)

def start_application():
    """Start the Flask application."""
    print("")
    print("=" * 40)
    print("To-Do List Application")
    print("=" * 40)
    print("")
    print("Starting server on http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("")
    
    python_exec = get_python_executable()
    
    if not os.path.exists("app.py"):
        print("Error: app.py not found")
        sys.exit(1)
    
    # Run the Flask app
    run_command([python_exec, "app.py"])

def main():
    """Main entry point."""
    print("Starting To-Do List Application...")
    print("")
    
    # Create virtual environment if needed
    create_venv()
    
    # Install dependencies
    install_dependencies()
    
    # Initialize database if needed
    initialize_database()
    
    # Start the application
    start_application()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
