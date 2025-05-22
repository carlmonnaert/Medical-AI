#!/usr/bin/env python3
"""
Main entry point for the hospital simulation system.

This script can start the simulation, dashboard, or both in separate processes.
"""

import argparse
import subprocess
import sys
import os
import time
from pathlib import Path

# Ensure we can import from src
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data.db import init_database
from src.config import DASHBOARD_PORT

def run_simulation(args):
    """Run the hospital simulation with the given arguments."""
    cmd = [sys.executable, "src/run_simulation.py"]
    
    if args.resume:
        cmd.append("--resume")
    if args.doctors:
        cmd.append(f"--doctors={args.doctors}")
    if args.rate:
        cmd.append(f"--rate={args.rate}")
    if args.minutes:
        cmd.append(f"--minutes={args.minutes}")
    
    print(f"Starting simulation: {' '.join(cmd)}")
    return subprocess.Popen(cmd)

def run_dashboard():
    """Run the dashboard application."""
    cmd = [sys.executable, "src/run_dashboard.py"]
    print(f"Starting dashboard server: {' '.join(cmd)}")
    print(f"Dashboard will be available at: http://localhost:{DASHBOARD_PORT}")
    return subprocess.Popen(cmd)

def run_ml(args):
    """Run the ML training and prediction."""
    cmd = [sys.executable, "src/run_ml.py"]
    
    if args.train:
        cmd.append("--train")
    if args.predict:
        cmd.append("--predict")
    if args.days:
        cmd.append(f"--days={args.days}")
    
    print(f"Starting ML operations: {' '.join(cmd)}")
    return subprocess.Popen(cmd)

def main():
    """Main entry point for the hospital simulation system."""
    parser = argparse.ArgumentParser(description="Hospital Simulation System")
    
    # Mode selection
    mode_group = parser.add_argument_group("Mode")
    mode_group.add_argument("--simulation", action="store_true", help="Run the simulation")
    mode_group.add_argument("--dashboard", action="store_true", help="Run the dashboard")
    mode_group.add_argument("--ml", action="store_true", help="Run ML operations")
    mode_group.add_argument("--all", action="store_true", help="Run all components")
    
    # Simulation options
    sim_group = parser.add_argument_group("Simulation Options")
    sim_group.add_argument("--resume", action="store_true", help="Resume from last saved state")
    sim_group.add_argument("--doctors", type=int, help="Number of doctors")
    sim_group.add_argument("--rate", type=float, help="Patient arrival rate")
    sim_group.add_argument("--minutes", type=int, help="Simulation duration in minutes")
    
    # ML options
    ml_group = parser.add_argument_group("ML Options")
    ml_group.add_argument("--train", action="store_true", help="Train ML models")
    ml_group.add_argument("--predict", action="store_true", help="Generate predictions")
    ml_group.add_argument("--days", type=int, help="Days to predict")
    
    args = parser.parse_args()
    
    # Initialize database
    print("Initializing database...")
    init_database()
    
    processes = []
    
    # Determine what to run
    run_sim = args.simulation or args.all
    run_dash = args.dashboard or args.all
    run_ml_ops = args.ml or args.all
    
    # If no mode specified, use interactive mode
    if not (run_sim or run_dash or run_ml_ops):
        print("\nNo mode specified. Starting interactive mode.")
        print("What would you like to run?")
        print("1. Simulation")
        print("2. Dashboard")
        print("3. ML operations")
        print("4. All components")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            run_sim = True
        elif choice == "2":
            run_dash = True
        elif choice == "3":
            run_ml_ops = True
        elif choice == "4":
            run_sim = True
            run_dash = True
            run_ml_ops = True
        else:
            print("Exiting.")
            return
    
    # Start components
    try:
        if run_sim:
            sim_process = run_simulation(args)
            processes.append(sim_process)
        
        if run_dash:
            # Give the simulation a moment to start if running both
            if run_sim:
                time.sleep(2)
            dash_process = run_dashboard()
            processes.append(dash_process)
        
        if run_ml_ops:
            # If not explicitly set, default to both train and predict
            if not (args.train or args.predict):
                args.train = True
                args.predict = True
            
            ml_process = run_ml(args)
            processes.append(ml_process)
        
        # Wait for all processes to complete
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down...")
        for process in processes:
            process.terminate()
    finally:
        # Make sure all processes are terminated
        for process in processes:
            try:
                process.terminate()
            except:
                pass

if __name__ == "__main__":
    main()