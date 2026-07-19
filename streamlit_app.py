"""
Streamlit Community Cloud Entry Point
This file is used for deployment on Streamlit Community Cloud.
It simply imports and runs the main app.
"""
import sys
import os

# Add project root to path (for local testing)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main app
from app import *
