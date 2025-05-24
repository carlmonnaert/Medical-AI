"""
Database utilities for hospital simulation.

This module provides functions for database initialization and access.
"""

import sqlite3
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.config import DB_PATH

def init_database() -> None:
    """Initialize SQLite database with required tables for the hospital simulation.
    
    Creates tables for patient treatments, hospital state, and simulation metadata if they don't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create simulations table to track different simulation runs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS simulations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TEXT,
        config TEXT,
        num_doctors INTEGER,
        arrival_rate REAL,
        description TEXT
    )
    ''')
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patient_treated (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sim_id INTEGER,
        doctor_id INTEGER,
        doctor_specialty TEXT,
        disease TEXT,
        treatment_time INTEGER,
        wait_time INTEGER,
        arrival_time TEXT,
        start_treatment TEXT,
        end_treatment TEXT,
        sim_minutes REAL,
        timestamp TEXT,
        FOREIGN KEY (sim_id) REFERENCES simulations (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hospital_state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sim_id INTEGER,
        patients_total INTEGER,
        patients_treated INTEGER,
        busy_doctors INTEGER,
        waiting_patients INTEGER,
        sim_time TEXT,
        sim_minutes REAL,
        timestamp TEXT,
        FOREIGN KEY (sim_id) REFERENCES simulations (id)
    )
    ''')
    
    # Add a simulation metadata table to store the current state for resuming
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sim_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sim_id INTEGER,
        start_date TEXT,
        last_sim_time REAL,
        patients_total INTEGER,
        patients_treated INTEGER,
        active_doctors TEXT,
        timestamp TEXT,
        FOREIGN KEY (sim_id) REFERENCES simulations (id)
    )
    ''')
    
    # Create a table for simulation events (patient flow, doctor assignments, etc.)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS simulation_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sim_id INTEGER,
        event_id TEXT,
        event_type TEXT,
        params TEXT,
        start_time TEXT,
        end_time TEXT,
        start_sim_minutes REAL,
        end_sim_minutes REAL,
        timestamp TEXT,
        FOREIGN KEY (sim_id) REFERENCES simulations (id)
    )
    ''')
    
    # Create a table for parameter changes during simulation
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parameter_changes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sim_id INTEGER,
        sim_time TEXT,
        sim_minutes REAL,
        old_values TEXT,
        new_values TEXT,
        timestamp TEXT,
        FOREIGN KEY (sim_id) REFERENCES simulations (id)
    )
    ''')
    
    # Create a table for detailed simulation events (arrivals, treatments, etc.)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS detailed_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sim_id INTEGER,
        event_type TEXT,
        patient_id TEXT,
        doctor_id INTEGER,
        event_time TEXT,
        sim_minutes REAL,
        details TEXT,
        timestamp TEXT,
        FOREIGN KEY (sim_id) REFERENCES simulations (id)
    )
    ''')
    
    # Create a table for ML model predictions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sim_id INTEGER,
        prediction_date TEXT,
        prediction_type TEXT,
        value REAL,
        confidence REAL,
        model_name TEXT,
        features TEXT,
        timestamp TEXT,
        FOREIGN KEY (sim_id) REFERENCES simulations (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection() -> sqlite3.Connection:
    """Connect to the SQLite database and set up row factory.
    
    Returns:
        sqlite3.Connection: An open connection to the database with row_factory set
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_new_simulation(num_doctors: int, arrival_rate: float, description: str = "") -> int:
    """Create a new simulation record and return its ID.
    
    Args:
        num_doctors: Number of doctors in the simulation
        arrival_rate: Patient arrival rate per hour
        description: Optional description of this simulation run
        
    Returns:
        int: ID of the newly created simulation record
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    config = json.dumps({
        "num_doctors": num_doctors,
        "arrival_rate": arrival_rate,
        "start_time": datetime.now().isoformat()
    })
    
    cursor.execute(
        "INSERT INTO simulations (start_time, config, num_doctors, arrival_rate, description) VALUES (?, ?, ?, ?, ?)",
        (datetime.now().isoformat(), config, num_doctors, arrival_rate, description)
    )
    
    sim_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return sim_id

def get_latest_simulation_id() -> Optional[int]:
    """Get the ID of the most recent simulation run.
    
    Returns:
        int: ID of the most recent simulation, or None if no simulations exist
    """
    conn = get_db_connection()
    result = conn.execute("SELECT id FROM simulations ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    
    if result:
        return result['id']
    return None

def get_all_simulation_ids() -> List[Dict[str, Any]]:
    """Get all simulation IDs and their basic information.
    
    Returns:
        List[Dict]: List of dictionaries containing simulation info
    """
    conn = get_db_connection()
    result = conn.execute("""
        SELECT id, start_time, num_doctors, arrival_rate, description 
        FROM simulations 
        ORDER BY id DESC
    """).fetchall()
    conn.close()
    
    simulations = []
    for row in result:
        simulations.append({
            'id': row['id'],
            'start_time': row['start_time'],
            'num_doctors': row['num_doctors'],
            'arrival_rate': row['arrival_rate'],
            'description': row['description']
        })
    
    return simulations

def get_simulation_by_id(sim_id: int) -> Optional[Dict[str, Any]]:
    """Get simulation information by ID.
    
    Args:
        sim_id: Simulation ID to look up
        
    Returns:
        Dict containing simulation info, or None if not found
    """
    conn = get_db_connection()
    result = conn.execute("""
        SELECT * FROM simulations WHERE id = ?
    """, (sim_id,)).fetchone()
    conn.close()
    
    if result:
        return dict(result)
    return None

def optimize_database_performance():
    """Apply SQLite performance optimizations for better Linux performance."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable WAL mode for better concurrent access
    cursor.execute("PRAGMA journal_mode=WAL")
    # Increase cache size (10MB cache)
    cursor.execute("PRAGMA cache_size=10000")
    # Reduce synchronization for speed
    cursor.execute("PRAGMA synchronous=NORMAL")
    # Memory temp store
    cursor.execute("PRAGMA temp_store=MEMORY")
    # Increase page size for better I/O
    cursor.execute("PRAGMA page_size=4096")
    
    conn.commit()
    conn.close()