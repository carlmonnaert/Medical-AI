"""
Machine learning models for hospital data prediction.

This module provides machine learning models for various prediction tasks:
- Patient arrival rate prediction
- Wait time prediction
- Disease outbreak prediction
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import sqlite3

from src.data.db import get_db_connection
from src.config import DB_PATH

class PatientArrivalModel:
    """Predicts patient arrival rates based on historical data.
    
    This model uses time-based features like hour of day, day of week,
    month, and special dates to predict expected arrival rates.
    
    Attributes:
        model: The trained prediction model
        features: List of features used by the model
    """
    
    def __init__(self):
        """Initialize the patient arrival model."""
        self.model = None
        self.features = [
            'hour_of_day', 'day_of_week', 'month', 
            'is_weekend', 'is_holiday', 'is_special_date'
        ]
    
    def train(self, db_path: str = DB_PATH) -> None:
        """Train the model using historical data from the database.
        
        Args:
            db_path: Path to the SQLite database with historical data
        """
        # Get the data
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(
            "SELECT arrival_time, COUNT(*) as count "
            "FROM patient_treated "
            "GROUP BY strftime('%Y-%m-%d %H', arrival_time)",
            conn
        )
        conn.close()
        
        if df.empty:
            print("No data available for training")
            return
        
        # Convert arrival_time to datetime
        df['arrival_time'] = pd.to_datetime(df['arrival_time'])
        
        # Extract features
        df['hour_of_day'] = df['arrival_time'].dt.hour
        df['day_of_week'] = df['arrival_time'].dt.dayofweek
        df['month'] = df['arrival_time'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # TODO: Add special date and holiday detection
        df['is_holiday'] = 0
        df['is_special_date'] = 0
        
        # Here you would train your model
        # For now, we'll just create a simple baseline model that 
        # calculates average arrivals by hour, day of week, and month
        self.hourly_avg = df.groupby('hour_of_day')['count'].mean()
        self.daily_avg = df.groupby('day_of_week')['count'].mean()
        self.monthly_avg = df.groupby('month')['count'].mean()
        self.overall_avg = df['count'].mean()
        
        print("Model trained successfully")
    
    def predict(self, date: datetime) -> float:
        """Predict patient arrival rate for a given date and time.
        
        Args:
            date: The date and time to predict for
            
        Returns:
            float: Predicted number of patient arrivals per hour
        """
        if self.hourly_avg is None:
            return 0  # Model not trained
        
        # Extract features from the date
        hour = date.hour
        day_of_week = date.weekday()
        month = date.month
        
        # Simple baseline prediction using historical averages
        hour_factor = self.hourly_avg.get(hour, self.overall_avg) / self.overall_avg
        day_factor = self.daily_avg.get(day_of_week, self.overall_avg) / self.overall_avg
        month_factor = self.monthly_avg.get(month, self.overall_avg) / self.overall_avg
        
        # Combine factors and scale by overall average
        prediction = self.overall_avg * hour_factor * day_factor * month_factor
        
        return prediction
    
    def save_predictions(self, start_date: datetime, days: int = 7, db_path: str = DB_PATH) -> None:
        """Generate and save predictions for a future time period.
        
        Args:
            start_date: Starting date for predictions
            days: Number of days to predict for
            db_path: Database path to save predictions
        """
        if self.hourly_avg is None:
            print("Model not trained, cannot make predictions")
            return
        
        predictions = []
        current_date = start_date
        end_date = start_date + timedelta(days=days)
        
        # Generate hourly predictions
        while current_date < end_date:
            predicted_value = self.predict(current_date)
            predictions.append({
                'prediction_date': current_date.isoformat(),
                'prediction_type': 'patient_arrivals',
                'value': predicted_value,
                'confidence': 0.8,  # Placeholder
                'model_name': 'PatientArrivalModel_v1',
                'features': ','.join(self.features),
                'timestamp': datetime.now().isoformat()
            })
            current_date += timedelta(hours=1)
        
        # Save to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for pred in predictions:
            cursor.execute('''
            INSERT INTO predictions 
            (prediction_date, prediction_type, value, confidence, model_name, features, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                pred['prediction_date'],
                pred['prediction_type'],
                pred['value'],
                pred['confidence'],
                pred['model_name'],
                pred['features'],
                pred['timestamp']
            ))
        
        conn.commit()
        conn.close()
        
        print(f"Saved {len(predictions)} predictions to database")