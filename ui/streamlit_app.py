"""
Streamlit Cloud entry point
This file imports and runs the main application from extended_monitor.py
"""
import sys
import os

# Add parent directory to path so imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the main app - this will execute all the code in extended_monitor.py
from ui import extended_monitor
