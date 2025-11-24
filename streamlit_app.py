"""
Streamlit Cloud entry point
This file should be at the root of the repository for Streamlit Cloud deployment
"""
import sys
import os

# Add the current directory to path to ensure all imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Initialize database if it doesn't exist
try:
    from database.db_manager import db_manager
    db_manager.init_db()
except Exception as e:
    print(f"Warning: Could not initialize database: {e}")

# Import and run the main application
from ui.extended_monitor import main

if __name__ == "__main__":
    main()

