"""
Visualization functions for the dashboard.

This module provides functions to generate visualizations for the dashboard.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from flask import jsonify
from typing import Dict, Any

from src.data.db import get_db_connection


def plot_diseases():
    """Generate a Plotly visualization for disease distribution.
    
    Returns:
        Response: JSON object with Plotly figure for disease distribution
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
    
    # Query for this specific simulation
    df = pd.read_sql_query(
        'SELECT disease, COUNT(*) as count FROM patient_treated WHERE sim_id = ? GROUP BY disease',
        conn, params=(sim_id,)
    )
    conn.close()
    
    if df.empty:
        return jsonify({'error': 'No data available'})
    
    # Use the latest Plotly Express for pie charts
    fig = px.pie(
        df, 
        values='count', 
        names='disease', 
        title='Disease Distribution',
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    
    return jsonify({
        'plot': json.loads(fig.to_json())
    })


def plot_timeline():
    """Generate a Plotly visualization for hospital state over time.
    
    Creates a line chart showing key metrics changing over the simulation period.
    
    Returns:
        Response: JSON object with Plotly figure for timeline visualization
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
    
    # Query for this specific simulation
    df = pd.read_sql_query(
        'SELECT sim_time, patients_total, patients_treated, busy_doctors, waiting_patients FROM hospital_state WHERE sim_id = ? ORDER BY sim_minutes',
        conn, params=(sim_id,)
    )
    conn.close()
    
    if df.empty:
        return jsonify({'error': 'No data available'})
    
    # Convert ISO datetime strings to datetime objects for proper plotting
    df['sim_time'] = pd.to_datetime(df['sim_time'])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['sim_time'], y=df['patients_total'], mode='lines', name='Total Patients'))
    fig.add_trace(go.Scatter(x=df['sim_time'], y=df['patients_treated'], mode='lines', name='Treated Patients'))
    fig.add_trace(go.Scatter(x=df['sim_time'], y=df['busy_doctors'], mode='lines', name='Busy Doctors'))
    fig.add_trace(go.Scatter(x=df['sim_time'], y=df['waiting_patients'], mode='lines', name='Waiting Patients'))
    
    fig.update_layout(
        title='Hospital Activity Over Time', 
        xaxis_title='Date and Time',
        yaxis_title='Count',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    fig.update_xaxes(tickformat="%Y-%m-%d %H:%M")
    
    return jsonify({
        'plot': json.loads(fig.to_json())
    })


def plot_hourly_pattern():
    """Generate a Plotly visualization for hourly arrival patterns.
    
    Creates a dual-axis chart showing both patient arrivals and wait times by hour of day.
    
    Returns:
        Response: JSON object with Plotly figure for hourly patterns
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
    
    # Get arrivals by hour of day for this simulation
    df = pd.read_sql_query(
        "SELECT strftime('%H', arrival_time) as hour, COUNT(*) as count FROM patient_treated WHERE sim_id = ? GROUP BY hour ORDER BY hour",
        conn, params=(sim_id,)
    )
    
    # Get wait times by hour for this simulation
    df_wait = pd.read_sql_query(
        "SELECT strftime('%H', arrival_time) as hour, AVG(wait_time) as avg_wait FROM patient_treated WHERE sim_id = ? GROUP BY hour ORDER BY hour",
        conn, params=(sim_id,)
    )
    
    conn.close()
    
    if df.empty:
        return jsonify({'error': 'No data available'})
    
    # Create hourly pattern visualization
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['hour'], 
        y=df['count'], 
        name='Patient Arrivals',
        marker_color='rgb(55, 83, 109)'
    ))
    
    # Add a secondary y-axis for wait times
    fig.add_trace(go.Scatter(
        x=df_wait['hour'], 
        y=df_wait['avg_wait'], 
        name='Average Wait Time (min)',
        mode='lines+markers',
        yaxis='y2',
        line=dict(color='rgb(214, 39, 40)', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Patient Arrivals and Wait Times by Hour of Day',
        xaxis_title='Hour of Day',
        yaxis_title='Number of Patients',
        template='plotly_white',
        yaxis2=dict(
            title='Average Wait Time (minutes)',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return jsonify({
        'plot': json.loads(fig.to_json())
    })


def plot_seasonal_pattern():
    """Generate a Plotly visualization for seasonal disease patterns.
    
    Creates a stacked bar chart showing disease prevalence by month of the year.
    
    Returns:
        Response: JSON object with Plotly figure for seasonal patterns
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
    
    # Get disease distribution by month for this simulation
    df = pd.read_sql_query(
        "SELECT strftime('%m', arrival_time) as month, disease, COUNT(*) as count FROM patient_treated WHERE sim_id = ? GROUP BY month, disease",
        conn, params=(sim_id,)
    )
    
    conn.close()
    
    if df.empty:
        return jsonify({'error': 'No data available'})
    
    # Convert month numbers to names for better display
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df['month_name'] = df['month'].astype(int).apply(lambda x: month_names[x-1] if 1 <= x <= 12 else f"Month {x}")
    
    # Create a pivot table for better visualization
    pivot_df = df.pivot_table(index='month_name', columns='disease', values='count', fill_value=0)
    
    # Ensure months are in correct order
    if not pivot_df.empty:
        month_order = [month_names[i-1] for i in range(1, 13) if month_names[i-1] in pivot_df.index]
        pivot_df = pivot_df.reindex(month_order)
    
    # Create the visualization with newer Plotly features
    fig = px.bar(
        pivot_df, 
        barmode='stack',
        title='Disease Distribution by Month',
        color_discrete_sequence=px.colors.qualitative.Bold,
        template='plotly_white'
    )
    
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Number of Patients',
        legend_title='Disease',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12
        )
    )
    
    return jsonify({
        'plot': json.loads(fig.to_json())
    })