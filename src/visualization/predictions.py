"""
Prediction visualization module.

This module provides functions for visualizing ML predictions in the dashboard.
"""

import pandas as pd
import plotly.graph_objects as go
import json
from flask import jsonify
from datetime import datetime, timedelta

from src.data.db import get_db_connection

def plot_arrival_predictions():
    """Generate a Plotly visualization of arrival predictions vs actual data.
    
    Returns:
        Response: JSON object with Plotly figure for predictions visualization
    """
    conn = get_db_connection()
    
    # Get simulation ID from request or use latest
    from flask import request
    from src.visualization.routes import get_latest_sim_id
    
    sim_id = request.args.get('sim_id', type=int)
    if not sim_id:
        sim_id = get_latest_sim_id()
        if not sim_id:
            return jsonify({'error': 'No simulation data available'})
    
    # Get predictions for this simulation
    pred_df = pd.read_sql_query(
        "SELECT prediction_date, value FROM predictions WHERE sim_id = ? AND prediction_type = 'patient_arrivals' ORDER BY prediction_date",
        conn, params=(sim_id,)
    )
    
    # Get actual patient arrivals (if available) for this simulation
    actual_df = pd.read_sql_query(
        "SELECT strftime('%Y-%m-%d %H:00:00', arrival_time) as hour, COUNT(*) as count " +
        "FROM patient_treated " +
        "WHERE sim_id = ? " +
        "GROUP BY strftime('%Y-%m-%d %H', arrival_time) " +
        "ORDER BY hour",
        conn, params=(sim_id,)
    )
    
    conn.close()
    
    if pred_df.empty:
        return jsonify({'error': 'No prediction data available'})
    
    # Convert to datetime for proper plotting
    pred_df['prediction_date'] = pd.to_datetime(pred_df['prediction_date'])
    if not actual_df.empty:
        actual_df['hour'] = pd.to_datetime(actual_df['hour'])
    
    # Create the visualization
    fig = go.Figure()
    
    # Add predictions
    fig.add_trace(go.Scatter(
        x=pred_df['prediction_date'], 
        y=pred_df['value'],
        mode='lines',
        name='Predicted Arrivals',
        line=dict(color='blue', dash='dash', width=2)
    ))
    
    # Add actual data if available
    if not actual_df.empty:
        fig.add_trace(go.Scatter(
            x=actual_df['hour'], 
            y=actual_df['count'],
            mode='lines',
            name='Actual Arrivals',
            line=dict(color='green', width=2)
        ))
    
    # Calculate prediction period
    if len(pred_df) > 0:
        min_date = pred_df['prediction_date'].min()
        max_date = pred_df['prediction_date'].max()
        title_suffix = f" ({min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')})"
    else:
        title_suffix = ""
    
    fig.update_layout(
        title=f'Patient Arrival Predictions{title_suffix}',
        xaxis_title='Date and Time',
        yaxis_title='Patients per Hour',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12
        )
    )
    
    return jsonify({
        'plot': json.loads(fig.to_json())
    })