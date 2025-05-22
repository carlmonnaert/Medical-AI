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


@app.route('/timeline')
def timeline():
    """Timeline explorer page.
    
    Returns:
        str: Rendered HTML template for the timeline explorer
    """
    return render_template('timeline.html')


@app.route('/controls')
def controls():
    """Simulation controls page.
    
    Returns:
        str: Rendered HTML template for the simulation controls
    """
    return render_template('controls.html')


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
    """Get hospital state timeline data for a simulation.
    
    Query params:
        sim_id: ID of the simulation
    
    Returns:
        Response: JSON object with timeline data
    """
    conn = get_db_connection()
    
    # Get simulation ID from query param or use latest
    sim_id = request.args.get('sim_id', type=int)
    if not sim_id:
        sim_id = get_latest_sim_id()
        if not sim_id:
            return jsonify({'error': 'No simulation data available'})
    
    # Get timeline data for this simulation
    timeline = conn.execute(
        'SELECT sim_time, patients_total, patients_treated, busy_doctors, waiting_patients FROM hospital_state WHERE sim_id = ? ORDER BY sim_time',
        (sim_id,)
    ).fetchall()
    
    if not timeline:
        return jsonify({'error': 'No timeline data available for this simulation'})
    
    # Convert to list of dictionaries for JSON serialization
    result = []
    for row in timeline:
        result.append(dict(row))
    
    conn.close()
    
    return jsonify({
        'timeline': result
    })


@app.route('/api/timeline_state')
def get_timeline_state():
    """Get hospital state at a specific point in time.
    
    Query params:
        sim_id: ID of the simulation
        datetime: ISO-8601 datetime string (YYYY-MM-DDTHH:MM)
    
    Returns:
        Response: JSON object with hospital state data
    """
    conn = get_db_connection()
    
    # Get simulation ID from query param or use latest
    sim_id = request.args.get('sim_id', type=int)
    if not sim_id:
        sim_id = get_latest_sim_id()
        if not sim_id:
            return jsonify({'error': 'No simulation data available'})
    
    # Get datetime from query param
    datetime_str = request.args.get('datetime')
    if not datetime_str:
        return jsonify({'error': 'No datetime provided'})
    
    try:
        # Parse datetime string and ensure format is consistent
        from dateutil import parser
        target_time = parser.parse(datetime_str)
        
        # Format for DB comparison
        formatted_time = target_time.strftime('%Y-%m-%d %H:%M:00')
    except:
        return jsonify({'error': 'Invalid datetime format. Use ISO-8601 (YYYY-MM-DDTHH:MM)'})
    
    # Get nearest hospital state record for this time (either exact match or just before)
    state = conn.execute(
        'SELECT * FROM hospital_state WHERE sim_id = ? AND sim_time <= ? ORDER BY sim_time DESC LIMIT 1',
        (sim_id, formatted_time)
    ).fetchone()
    
    if not state:
        # Try to get the earliest record if no records are before the requested time
        state = conn.execute(
            'SELECT * FROM hospital_state WHERE sim_id = ? ORDER BY sim_time ASC LIMIT 1',
            (sim_id,)
        ).fetchone()
        
        if not state:
            return jsonify({'error': 'No hospital state data available for this simulation'})
        return jsonify({
            'error': 'No data available before the requested time. Showing earliest available state.',
            **dict(state),
            'free_doctors': state['total_doctors'] - state['busy_doctors']
        })
    
    # Convert SQLite row to dictionary and add free doctors calculation
    state_dict = dict(state)
    state_dict['free_doctors'] = state_dict['total_doctors'] - state_dict['busy_doctors']
    
    conn.close()
    
    return jsonify(state_dict)


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
    """API endpoint for timeline plot.
    
    Returns:
        Response: JSON object with Plotly figure for timeline visualization
    """
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


@app.route('/api/simulation/modify_parameters', methods=['POST'])
def modify_simulation_parameters():
    """Modify parameters of a running simulation.
    
    Request JSON:
        sim_id: ID of the simulation to modify
        parameters: Dictionary of parameters to update:
            - arrival_rate: New patient arrival rate
            - num_doctors: New doctor count
    
    Returns:
        Response: JSON object with result of the operation
    """
    from src.visualization.simulations import get_active_simulations
    
    # Get request data
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    sim_id = data.get('sim_id')
    parameters = data.get('parameters', {})
    
    if not sim_id:
        return jsonify({'error': 'Simulation ID is required'}), 400
    
    if not parameters:
        return jsonify({'error': 'No parameters provided for update'}), 400
    
    # Get active simulations
    active_sims = get_active_simulations()
    
    if sim_id not in active_sims:
        return jsonify({'error': 'Simulation not active or not found'}), 404
    
    # Get the simulation instance
    sim = active_sims[sim_id]
    
    # Update parameters
    success = sim.update_parameters(parameters)
    
    if success:
        return jsonify({
            'success': True, 
            'message': 'Parameters updated successfully',
            'sim_id': sim_id,
            'parameters': parameters
        })
    else:
        return jsonify({'error': 'Failed to update parameters'}), 500


@app.route('/api/simulation/add_event', methods=['POST'])
def add_simulation_event():
    """Add an event to a running simulation.
    
    Request JSON:
        sim_id: ID of the simulation
        event_type: Type of event (epidemic, disaster, weather)
        params: Parameters specific to the event type
        duration_minutes: How long the event should last (in simulation minutes)
    
    Returns:
        Response: JSON object with result of the operation
    """
    from src.visualization.simulations import get_active_simulations
    
    # Get request data
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    sim_id = data.get('sim_id')
    event_type = data.get('event_type')
    params = data.get('params', {})
    duration_minutes = data.get('duration_minutes', 1440)  # Default 24 hours
    
    if not sim_id:
        return jsonify({'error': 'Simulation ID is required'}), 400
    
    if not event_type:
        return jsonify({'error': 'Event type is required'}), 400
    
    # Get active simulations
    active_sims = get_active_simulations()
    
    if sim_id not in active_sims:
        return jsonify({'error': 'Simulation not active or not found'}), 404
    
    # Get the simulation instance
    sim = active_sims[sim_id]
    
    # Add event
    success = sim.add_event(event_type, params, duration_minutes)
    
    if success:
        return jsonify({
            'success': True, 
            'message': 'Event added successfully',
            'sim_id': sim_id,
            'event_type': event_type,
            'duration_minutes': duration_minutes
        })
    else:
        return jsonify({'error': 'Failed to add event'}), 500


@app.route('/api/simulation/active_events')
def get_active_events():
    """Get active events for a simulation.
    
    Query params:
        sim_id: ID of the simulation
    
    Returns:
        Response: JSON object with active events
    """
    from src.visualization.simulations import get_active_simulations
    
    # Get simulation ID from query param
    sim_id = request.args.get('sim_id', type=int)
    if not sim_id:
        return jsonify({'error': 'Simulation ID is required'}), 400
    
    # Get active simulations
    active_sims = get_active_simulations()
    
    if sim_id not in active_sims:
        return jsonify({'error': 'Simulation not active or not found'}), 404
    
    # Get the simulation instance
    sim = active_sims[sim_id]
    
    # Get active events
    events = []
    for event_id, event_data in sim.active_events.items():
        events.append({
            'id': event_id,
            'type': event_data['type'],
            'params': event_data['params'],
            'start_date': event_data['start_date'],
            'end_date': event_data['end_date']
        })
    
    return jsonify({'events': events})


@app.route('/api/simulation/parameter_history')
def get_parameter_history():
    """Get parameter change history for a simulation.
    
    Query params:
        sim_id: ID of the simulation
    
    Returns:
        Response: JSON object with parameter changes
    """
    # Get simulation ID from query param
    sim_id = request.args.get('sim_id', type=int)
    if not sim_id:
        return jsonify({'error': 'Simulation ID is required'}), 400
    
    # Connect to database
    conn = get_db_connection()
    
    # Get parameter changes
    changes = conn.execute(
        'SELECT sim_time, sim_minutes, old_values, new_values FROM parameter_changes WHERE sim_id = ? ORDER BY sim_minutes DESC',
        (sim_id,)
    ).fetchall()
    
    # Convert to list of dictionaries
    result = []
    for change in changes:
        result.append({
            'sim_date': change['sim_time'],
            'sim_minutes': change['sim_minutes'],
            'old_values': json.loads(change['old_values']),
            'new_values': json.loads(change['new_values'])
        })
    
    conn.close()
    
    return jsonify({'changes': result})


@app.route('/api/simulation/is_active')
def is_simulation_active():
    """Check if a simulation is active (database is changing).
    
    Query params:
        sim_id: ID of the simulation
        last_update_time: Last known database update timestamp (optional)
    
    Returns:
        Response: JSON object indicating if simulation is active and last update time
    """
    # Get simulation ID from query param
    sim_id = request.args.get('sim_id', type=int)
    if not sim_id:
        return jsonify({'error': 'Simulation ID is required'}), 400
    
    # Get optional last update time
    last_update_time = request.args.get('last_update_time')
    
    # Connect to database
    conn = get_db_connection()
    
    # Get latest hospital state timestamp for this simulation
    latest = conn.execute(
        'SELECT timestamp FROM hospital_state WHERE sim_id = ? ORDER BY id DESC LIMIT 1',
        (sim_id,)
    ).fetchone()
    
    # Check if this simulation is registered in active simulations
    from src.visualization.simulations import get_active_simulations
    active_sims = get_active_simulations()
    is_registered_active = sim_id in active_sims
    
    # Determine if there's new data
    has_new_data = False
    current_timestamp = latest['timestamp'] if latest else None
    
    if current_timestamp and last_update_time:
        # Check if the timestamp is newer than the provided last update
        has_new_data = current_timestamp != last_update_time
    
    conn.close()
    
    return jsonify({
        'sim_id': sim_id,
        'is_active': is_registered_active,
        'last_update_time': current_timestamp,
        'has_new_data': has_new_data
    })