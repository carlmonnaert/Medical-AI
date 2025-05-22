#!/usr/bin/env python3
"""
Train and run machine learning predictions.

This script trains the ML models and generates predictions based on simulation data.
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to Python path so 'src' can be imported
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.ml.models import PatientArrivalModel
from src.data.db import init_database
from src.config import DB_PATH

def main():
    """Main entry point for the ML training and prediction script."""
    parser = argparse.ArgumentParser(description="Train ML models and make predictions")
    parser.add_argument("--train", action="store_true", help="Train models on existing data")
    parser.add_argument("--predict", action="store_true", help="Generate predictions")
    parser.add_argument("--days", type=int, default=7, help="Number of days to predict")
    args = parser.parse_args()
    
    # Make sure DB exists and has the required tables
    init_database()
    
    print("Starting ML operations")
    
    # Initialize models
    arrival_model = PatientArrivalModel()
    
    # Train models if requested
    if args.train:
        print("Training patient arrival model...")
        arrival_model.train(db_path=DB_PATH)
    
    # Generate predictions if requested
    if args.predict:
        if not hasattr(arrival_model, 'hourly_avg') or arrival_model.hourly_avg is None:
            print("Model not trained. Training first...")
            arrival_model.train(db_path=DB_PATH)
        
        print(f"Generating predictions for the next {args.days} days...")
        start_date = datetime.now()
        arrival_model.save_predictions(start_date, days=args.days, db_path=DB_PATH)
        print("Predictions saved to database")

if __name__ == "__main__":
    main()