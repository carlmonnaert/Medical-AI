"""
Dashboard module for hospital simulation.

This module initializes the Flask application for the dashboard.
"""

from flask import Flask
import os

from src.config import DASHBOARD_DEBUG, DASHBOARD_PORT

# Create Flask app
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                         'src', 'templates'))

# Import routes and simulation management after creating app
from src.visualization import routes
from src.visualization import simulations