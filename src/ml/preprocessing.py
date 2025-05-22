"""
Data preprocessing and feature engineering module.

This module provides functions for preparing simulation data
for machine learning models, including feature extraction and transformation.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Any
import sqlite3
from datetime import datetime

from src.data.db import get_db_connection
from src.config import DB_PATH, SPECIAL_DATES


def load_patient_data(db_path: str = DB_PATH) -> pd.DataFrame:
    """Load patient data from the database.
    
    Args:
        db_path: Path to the SQLite database
        
    Returns:
        DataFrame: Patient data with added features
    """
    conn = sqlite3.connect(db_path)
    
    query = """
    SELECT 
        id, doctor_id, doctor_specialty, disease, 
        treatment_time, wait_time, 
        arrival_time, start_treatment, end_treatment, 
        sim_minutes
    FROM patient_treated
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        return df
    
    # Convert date strings to datetime
    for col in ['arrival_time', 'start_treatment', 'end_treatment']:
        df[col] = pd.to_datetime(df[col])
    
    # Extract time-based features
    df['hour_of_day'] = df['arrival_time'].dt.hour
    df['day_of_week'] = df['arrival_time'].dt.dayofweek
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['month'] = df['arrival_time'].dt.month
    df['day'] = df['arrival_time'].dt.day
    
    # Add special date indicator
    df['is_special_date'] = 0
    for special_date in SPECIAL_DATES:
        mask = (df['arrival_time'].dt.month == special_date['month']) & \
               (df['arrival_time'].dt.day == special_date['day'])
        df.loc[mask, 'is_special_date'] = 1
        df.loc[mask, 'special_date_factor'] = special_date['factor']
    
    return df


def create_hourly_aggregation(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate patient data by hour.
    
    Args:
        df: Patient dataframe
        
    Returns:
        DataFrame: Hourly aggregated metrics
    """
    if df.empty:
        return pd.DataFrame()
    
    # Create hour bins
    df['hour_bin'] = df['arrival_time'].dt.floor('H')
    
    # Aggregate by hour
    hourly = df.groupby('hour_bin').agg({
        'id': 'count',  # Number of patients
        'wait_time': ['mean', 'median', 'max'],  # Wait time stats
        'treatment_time': ['mean', 'median'],  # Treatment time stats
        'hour_of_day': 'first',
        'day_of_week': 'first',
        'is_weekend': 'first',
        'month': 'first',
        'is_special_date': 'max'
    })
    
    # Flatten column names
    hourly.columns = ['_'.join(col).strip() for col in hourly.columns.values]
    
    # Rename for clarity
    hourly.rename(columns={
        'id_count': 'patient_count',
        'wait_time_mean': 'avg_wait_time',
        'treatment_time_mean': 'avg_treatment_time'
    }, inplace=True)
    
    return hourly


def split_train_test(df: pd.DataFrame, test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split data into training and testing sets, preserving time order.
    
    Args:
        df: DataFrame to split
        test_size: Fraction of data to use for testing
        
    Returns:
        Tuple of (train_df, test_df)
    """
    if df.empty:
        return df, df
    
    # Sort by time
    df = df.sort_index()
    
    # Split based on time
    split_idx = int(len(df) * (1 - test_size))
    train = df.iloc[:split_idx]
    test = df.iloc[split_idx:]
    
    return train, test


def prepare_features_targets(df: pd.DataFrame, 
                             target_col: str, 
                             feature_cols: List[str]) -> Tuple[np.ndarray, np.ndarray]:
    """Extract feature and target arrays for model training.
    
    Args:
        df: Input dataframe
        target_col: Name of the target column
        feature_cols: List of feature column names
        
    Returns:
        Tuple of (features_array, target_array)
    """
    if df.empty or target_col not in df.columns:
        return np.array([]), np.array([])
    
    # Filter to only needed columns
    available_features = [col for col in feature_cols if col in df.columns]
    
    X = df[available_features].values
    y = df[target_col].values
    
    return X, y