"""
Simulation management utility for the dashboard.

This module provides endpoints for managing multiple simulations in the dashboard.
"""

from flask import request, jsonify
from src.visualization.dashboard import app
from src.data.db import get_db_connection
import pandas as pd

@app.route('/api/simulations')
def get_simulations():
    """Get a list of all available simulations.
    
    Returns:
        Response: JSON object with list of simulations
    """
    conn = get_db_connection()
    
    # Get all simulations
    simulations = conn.execute(
        'SELECT id, start_time, num_doctors, arrival_rate, description FROM simulations ORDER BY id DESC'
    ).fetchall()
    
    # For each simulation, get some basic stats
    result = []
    for sim in simulations:
        sim_dict = dict(sim)
        
        # Get total patients
        patients = conn.execute(
            'SELECT COUNT(*) as count FROM patient_treated WHERE sim_id = ?',
            (sim_dict['id'],)
        ).fetchone()
        
        # Get average wait time
        wait_time = conn.execute(
            'SELECT AVG(wait_time) as avg_wait FROM patient_treated WHERE sim_id = ?',
            (sim_dict['id'],)
        ).fetchone()
        
        # Add stats to simulation dict
        sim_dict['total_patients'] = patients['count'] if patients else 0
        sim_dict['avg_wait_time'] = wait_time['avg_wait'] if wait_time and wait_time['avg_wait'] else 0
        
        result.append(sim_dict)
    
    conn.close()
    
    return jsonify({
        'simulations': result
    })

@app.route('/api/simulations/compare')
def compare_simulations():
    """Compare two or more simulations.
    
    Query params:
        sim_ids: Comma-separated list of simulation IDs to compare
    
    Returns:
        Response: JSON object with comparison data
    """
    sim_ids_param = request.args.get('sim_ids', '')
    if not sim_ids_param:
        return jsonify({'error': 'No simulation IDs provided'})
    
    try:
        sim_ids = [int(id.strip()) for id in sim_ids_param.split(',')]
    except ValueError:
        return jsonify({'error': 'Invalid simulation ID format'})
    
    if len(sim_ids) < 2:
        return jsonify({'error': 'At least two simulation IDs are required for comparison'})
    
    conn = get_db_connection()
    
    # Get basic info for each simulation
    sims_info = []
    for sim_id in sim_ids:
        sim = conn.execute(
            'SELECT id, num_doctors, arrival_rate FROM simulations WHERE id = ?',
            (sim_id,)
        ).fetchone()
        
        if sim:
            sims_info.append(dict(sim))
    
    # Get comparison metrics
    comparison = {
        'wait_times': [],
        'treatment_counts': [],
        'doctor_utilization': []
    }
    
    # Wait time comparison
    for sim_id in sim_ids:
        wait_time = conn.execute(
            'SELECT sim_id, AVG(wait_time) as avg_wait FROM patient_treated WHERE sim_id = ?',
            (sim_id,)
        ).fetchone()
        
        if wait_time:
            comparison['wait_times'].append({
                'sim_id': sim_id,
                'avg_wait': wait_time['avg_wait'] if wait_time['avg_wait'] else 0
            })
    
    # Treatment count comparison
    for sim_id in sim_ids:
        treatments = conn.execute(
            'SELECT sim_id, COUNT(*) as count FROM patient_treated WHERE sim_id = ?',
            (sim_id,)
        ).fetchone()
        
        if treatments:
            comparison['treatment_counts'].append({
                'sim_id': sim_id,
                'count': treatments['count']
            })
    
    # Doctor utilization comparison (based on percentage of busy doctors)
    for sim_id in sim_ids:
        # Get average percentage of busy doctors
        utilization = conn.execute(
            'SELECT sim_id, AVG(busy_doctors * 100.0 / ?) as utilization FROM hospital_state WHERE sim_id = ?',
            (sims_info[sim_ids.index(sim_id)]['num_doctors'], sim_id)
        ).fetchone()
        
        if utilization:
            comparison['doctor_utilization'].append({
                'sim_id': sim_id,
                'utilization': utilization['utilization'] if utilization['utilization'] else 0
            })
    
    conn.close()
    
    return jsonify({
        'simulations': sims_info,
        'comparison': comparison
    })