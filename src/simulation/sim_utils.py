#!/usr/bin/env python3
"""
Hospital simulation utility script.

This script provides utilities for managing and testing the hospital simulation.
"""

import argparse
import simpy
from datetime import datetime
from src.data.db import init_database, get_all_simulation_ids
from src.simulation.hospital_sim import HospitalSim

def list_simulations():
    """List all available simulations in the database."""
    simulations = get_all_simulation_ids()
    if not simulations:
        print("No simulations found in the database.")
        return
    
    print("Available simulations:")
    print("ID | Start Time           | Doctors | Arrival Rate | Description")
    print("---|---------------------|---------|--------------|-------------")
    for sim in simulations:
        print(f"{sim['id']:2d} | {sim['start_time'][:19]} | {sim['num_doctors']:7d} | {sim['arrival_rate']:12.1f} | {sim['description']}")

def run_new_simulation(num_doctors: int = 30, arrival_rate: float = 20, duration: int = 1440):
    """Run a new simulation.
    
    Args:
        num_doctors: Number of doctors in the hospital
        arrival_rate: Patient arrival rate per hour
        duration: Simulation duration in minutes (default: 1 day)
    """
    print(f"Starting new simulation with {num_doctors} doctors, {arrival_rate} arrivals/hour for {duration} minutes...")
    
    # Initialize database if needed
    init_database()
    
    # Create SimPy environment
    env = simpy.Environment()
    
    # Create and run simulation
    sim = HospitalSim(env, num_doctors=num_doctors, arrival_rate=arrival_rate)
    print(f"Created simulation with ID: {sim.sim_id}")
    
    try:
        sim.run(duration)
        print(f"Simulation completed. Total patients: {sim.patients_total}, Treated: {sim.patients_treated}")
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    except Exception as e:
        print(f"Error during simulation: {e}")

def resume_simulation(sim_id: int, duration: int = 1440):
    """Resume an existing simulation.
    
    Args:
        sim_id: ID of the simulation to resume
        duration: Additional simulation duration in minutes
    """
    print(f"Resuming simulation {sim_id} for {duration} minutes...")
    
    # Create SimPy environment
    env = simpy.Environment()
    
    # Create and resume simulation
    try:
        sim = HospitalSim(env, resume=True, resume_sim_id=sim_id)
        
        # Get current state before running
        initial_time = env.now
        initial_patients = sim.patients_total
        
        print(f"Resuming from simulation time: {initial_time} minutes")
        print(f"Initial state: {initial_patients} patients processed")
        
        # Run for additional time - calculate target end time
        target_time = initial_time + duration
        print(f"Running until simulation time: {target_time} minutes")
        
        sim.run(target_time)
        
        print(f"Simulation completed. Total patients: {sim.patients_total}, Treated: {sim.patients_treated}")
        print(f"New patients in this session: {sim.patients_total - initial_patients}")
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    except Exception as e:
        print(f"Error during simulation: {e}")

def test_events(sim_id: int = None):
    """Test adding events to a simulation.
    
    Args:
        sim_id: ID of simulation to add events to (creates new if None)
    """
    env = simpy.Environment()
    
    if sim_id:
        print(f"Adding events to existing simulation {sim_id}")
        sim = HospitalSim(env, resume=True, resume_sim_id=sim_id)
        # Get the current time to calculate target
        initial_time = env.now
        target_time = initial_time + 1440  # Run for 24 hours from current position
    else:
        print("Creating new simulation for event testing")
        sim = HospitalSim(env, num_doctors=20, arrival_rate=15)
        target_time = 1440  # Run for 24 hours from start
    
    # Add some test events
    print("Adding test events...")
    
    # Add an epidemic event
    epidemic_params = {
        'disease': 'viral_infection',
        'arrival_factor': 2.0,
        'disease_factor': 4.0,
        'treatment_time_factor': 1.3
    }
    sim.add_event('epidemic', epidemic_params, duration_minutes=480)  # 8 hours
    
    # Add a disaster event
    disaster_params = {
        'arrival_factor': 1.8,
        'fracture_factor': 3.0,
        'trauma_factor': 4.0
    }
    sim.add_event('disaster', disaster_params, duration_minutes=240)  # 4 hours
    
    # Add weather event
    weather_params = {
        'weather_type': 'cold'
    }
    sim.add_event('weather', weather_params, duration_minutes=720)  # 12 hours
    
    print("Running simulation with events for 24 hours...")
    try:
        sim.run(target_time)
        print(f"Event test completed. Total patients: {sim.patients_total}, Treated: {sim.patients_treated}")
    except Exception as e:
        print(f"Error during event test: {e}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Hospital Simulation Utility')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List simulations command
    list_parser = subparsers.add_parser('list', help='List all simulations')
    
    # New simulation command
    new_parser = subparsers.add_parser('new', help='Run a new simulation')
    new_parser.add_argument('--doctors', type=int, default=30, help='Number of doctors (default: 30)')
    new_parser.add_argument('--arrival-rate', type=float, default=20, help='Arrival rate per hour (default: 20)')
    new_parser.add_argument('--duration', type=int, default=1440, help='Duration in minutes (default: 1440 = 1 day)')
    
    # Resume simulation command
    resume_parser = subparsers.add_parser('resume', help='Resume an existing simulation')
    resume_parser.add_argument('sim_id', type=int, help='Simulation ID to resume')
    resume_parser.add_argument('--duration', type=int, default=1440, help='Additional duration in minutes (default: 1440)')
    
    # Test events command
    events_parser = subparsers.add_parser('events', help='Test events functionality')
    events_parser.add_argument('--sim-id', type=int, help='Simulation ID to add events to (creates new if not specified)')
    
    # Initialize database command
    init_parser = subparsers.add_parser('init', help='Initialize the database')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_simulations()
    elif args.command == 'new':
        run_new_simulation(args.doctors, args.arrival_rate, args.duration)
    elif args.command == 'resume':
        resume_simulation(args.sim_id, args.duration)
    elif args.command == 'events':
        test_events(args.sim_id)
    elif args.command == 'init':
        init_database()
        print("Database initialized successfully.")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()