"""
Routes module for the dashboard.

This module defines all the routes for the Flask dashboard application.
"""

from flask import render_template, jsonify, request
import pandas as pd
import json
from typing import Dict, List, Union, Any

from src.visualization.dashboard import app
from src.data.db import get_db_connection
from src.visualization.plots import (
    plot_diseases, plot_timeline, plot_hourly_pattern, plot_seasonal_pattern
)
from src.visualization.predictions import plot_arrival_predictions


def get_latest_sim_id():
    """Get the most recent simulation ID.
    
    Returns:
        int: ID of the most recent simulation
    """
    conn = get_db_connection()
    sim = conn.execute('SELECT id FROM simulations ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()
    
    if sim:
        return sim['id']
    return None


@app.route('/')
def index():
    """Main dashboard page.
    
    Returns:
        str: Rendered HTML template for the dashboard
    """
    return render_template('index.html')


@app.route('/api/summary')
def get_summary():
    """Get summary statistics from the simulation.
    
    Retrieves various summary statistics including latest state,
    disease distribution, specialty distribution, and busy periods.
    
    Returns:
        Response: JSON object with summary statistics
    """
    conn = get_db_connection()
    
    # Get simulation ID from query param or use latest
    sim_id = request.args.get('sim_id', type=int)
    if not sim_id:
        sim_id = get_latest_sim_id()
        if not sim_id:
            return jsonify({'error': 'No simulations found'})
    
    # Get the latest hospital state for this simulation
    latest = conn.execute(
        'SELECT * FROM hospital_state WHERE sim_id = ? ORDER BY id DESC LIMIT 1',
        (sim_id,)
    ).fetchone()
    
    # Get disease distribution for this simulation
    diseases = conn.execute(
        'SELECT disease, COUNT(*) as count FROM patient_treated WHERE sim_id = ? GROUP BY disease',
        (sim_id,)
    ).fetchall()
    
    # Get specialty distribution for this simulation
    specialties = conn.execute(
        'SELECT doctor_specialty, COUNT(*) as count FROM patient_treated WHERE sim_id = ? GROUP BY doctor_specialty',
        (sim_id,)
    ).fetchall()
    
    # Get average wait time for this simulation
    avg_wait = conn.execute(
        'SELECT AVG(wait_time) as avg_wait FROM patient_treated WHERE sim_id = ?',
        (sim_id,)
    ).fetchone()
    
    # Get busiest hours for this simulation
    busiest_hours = conn.execute(
        "SELECT strftime('%H', arrival_time) as hour, COUNT(*) as count FROM patient_treated WHERE sim_id = ? GROUP BY hour ORDER BY count DESC LIMIT 3",
        (sim_id,)
    ).fetchall()
    
    # Get busiest days for this simulation
    busiest_days = conn.execute(
        "SELECT strftime('%w', arrival_time) as day, COUNT(*) as count FROM patient_treated WHERE sim_id = ? GROUP BY day ORDER BY count DESC LIMIT 3",
        (sim_id,)
    ).fetchall()
    
    conn.close()
    
    # Map day numbers to day names
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    busiest_days_named = []
    for day in busiest_days:
        day_dict = dict(day)
        day_dict['day_name'] = day_names[int(day_dict['day'])]
        busiest_days_named.append(day_dict)
    
    return jsonify({
        'sim_id': sim_id,
        'latest': dict(latest) if latest else {},
        'diseases': [dict(d) for d in diseases],
        'specialties': [dict(s) for s in specialties],
        'avg_wait_time': dict(avg_wait)['avg_wait'] if avg_wait else 0,
        'busiest_hours': [dict(h) for h in busiest_hours],
        'busiest_days': busiest_days_named
    })


@app.route('/api/timeline')
def get_timeline():
    """Get timeline data for charts.
    
    Returns:
        Response: JSON object with timeline data for visualization
    """
    conn = get_db_connection()
    
    # Get simulation ID from query param or use latest
    sim_id = request.args.get('sim_id', type=int)
    if not sim_id:
        sim_id = get_latest_sim_id()
        if not sim_id:
            return jsonify({'error': 'No simulations found'})
    
    # Get hospital state over time for this simulation
    timeline = conn.execute(
        'SELECT sim_time, sim_minutes, patients_total, patients_treated, busy_doctors, waiting_patients FROM hospital_state WHERE sim_id = ? ORDER BY sim_minutes',
        (sim_id,)
    ).fetchall()
    
    conn.close()
    
    return jsonify({
        'sim_id': sim_id,
        'timeline': [dict(t) for t in timeline],
    })


@app.route('/api/wait_times')
def get_wait_times():
    """Get wait time data by specialty and time period.
    
    Returns:
        Response: JSON object with wait time statistics by different parameters
    """
    conn = get_db_connection()
    
    # Get simulation ID from query param or use latest
    sim_id = request.args.get('sim_id', type=int)
    if not sim_id:
        sim_id = get_latest_sim_id()
        if not sim_id:
            return jsonify({'error': 'No simulations found'})
    
    # Get wait times by specialty for this simulation
    wait_times_by_specialty = conn.execute(
        'SELECT doctor_specialty, AVG(wait_time) as avg_wait FROM patient_treated WHERE sim_id = ? GROUP BY doctor_specialty',
        (sim_id,)
    ).fetchall()
    
    # Get wait times by hour of day for this simulation
    wait_times_by_hour = conn.execute(
        "SELECT strftime('%H', arrival_time) as hour, AVG(wait_time) as avg_wait FROM patient_treated WHERE sim_id = ? GROUP BY hour ORDER BY hour",
        (sim_id,)
    ).fetchall()
    
    # Get wait times by day of week (0=Monday, 6=Sunday) for this simulation
    wait_times_by_day = conn.execute(
        "SELECT strftime('%w', arrival_time) as day, AVG(wait_time) as avg_wait FROM patient_treated WHERE sim_id = ? GROUP BY day ORDER BY day",
        (sim_id,)
    ).fetchall()
    
    conn.close()
    
    return jsonify({
        'sim_id': sim_id,
        'wait_times_by_specialty': [dict(w) for w in wait_times_by_specialty],
        'wait_times_by_hour': [dict(w) for w in wait_times_by_hour],
        'wait_times_by_day': [dict(w) for w in wait_times_by_day],
    })


@app.route('/api/plot/diseases')
def api_plot_diseases():
    """API endpoint for disease distribution plot."""
    return plot_diseases()


@app.route('/api/plot/timeline')
def api_plot_timeline():
    """API endpoint for timeline plot."""
    return plot_timeline()


@app.route('/api/plot/hourly_pattern')
def api_plot_hourly_pattern():
    """API endpoint for hourly pattern plot."""
    return plot_hourly_pattern()


@app.route('/api/plot/seasonal_pattern')
def api_plot_seasonal_pattern():
    """API endpoint for seasonal pattern plot."""
    return plot_seasonal_pattern()


@app.route('/api/plot/predictions')
def api_plot_predictions():
    """API endpoint for arrival predictions plot."""
    return plot_arrival_predictions()