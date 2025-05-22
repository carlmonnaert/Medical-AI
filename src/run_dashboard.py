#!/usr/bin/env python3
"""
Dashboard runner script.

This script imports and starts the Flask dashboard application.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path so 'src' can be imported
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.visualization.dashboard import app
from src.visualization.routes import *  # This imports all routes
from src.config import DASHBOARD_DEBUG, DASHBOARD_PORT

def main():
    """Start the Flask dashboard application."""
    print(f"Starting dashboard on http://localhost:{DASHBOARD_PORT}")
    app.run(debug=DASHBOARD_DEBUG, port=DASHBOARD_PORT)

if __name__ == "__main__":
    main()