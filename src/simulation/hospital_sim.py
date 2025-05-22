"""
Hospital simulation core module.

This module provides the main HospitalSim class that handles the simulation logic.
"""

import simpy
import numpy as np
import random
import json
from datetime import datetime, timedelta
import sqlite3
from typing import List, Dict, Any, Optional

from src.config import (
    SIM_START_DATE, DISEASES, DISEASE_WEIGHTS, SPECIALTIES, 
    SPECIALTY_PROPORTIONS, SPECIAL_DATES, DB_PATH, 
    HOUR_FACTORS, DAY_FACTORS, MONTH_FACTORS,
    DEFAULT_NUM_DOCTORS, DEFAULT_ARRIVAL_RATE
)
from src.simulation.models import Doctor, Patient

class HospitalSim:
    """Hospital simulation model with various specialties and diseases.
    
    This class handles the main simulation logic including patient arrivals,
    doctor assignments, treatment, and data collection.
    
    Attributes:
        env (simpy.Environment): SimPy simulation environment
        num_doctors (int): Total number of doctors in the simulation
        arrival_rate (float): Avg number of patient arrivals per hour
        db_path (str): Path to SQLite database file
        resume (bool): Whether to resume from saved state
        patients_total (int): Total patients generated
        patients_treated (int): Total patients treated
        start_date (datetime): Simulation start date
        doctors (List[Doctor]): List of doctors in the hospital
    """
    
    def __init__(self, env: simpy.Environment, num_doctors: int = DEFAULT_NUM_DOCTORS, 
                 arrival_rate: float = DEFAULT_ARRIVAL_RATE, db_path: str = DB_PATH, resume: bool = False):
        """Initialize the hospital simulation.
        
        Args:
            env: SimPy environment
            num_doctors: Number of doctors in the hospital
            arrival_rate: Average patient arrivals per hour
            db_path: Path to SQLite database
            resume: Whether to resume from a previously saved state
        """
        self.env = env
        self.num_doctors = num_doctors
        self.arrival_rate = arrival_rate
        self.db_path = db_path
        self.resume = resume
        
        # Default start values
        self.patients_total = 0
        self.patients_treated = 0
        self.start_date = SIM_START_DATE
        
        # Create or get simulation ID
        from src.data.db import create_new_simulation, get_latest_simulation_id
        if resume:
            # Get the latest simulation ID if resuming
            self.sim_id = get_latest_simulation_id()
            if self.sim_id is None:
                print("No previous simulation found. Starting a new simulation.")
                self.sim_id = create_new_simulation(num_doctors, arrival_rate, "Resumed simulation")
                self.resume = False
        else:
            # Create a new simulation record
            self.sim_id = create_new_simulation(num_doctors, arrival_rate, "New simulation")
        
        # If resuming, try to load state
        if resume:
            self._load_simulation_state()
        
        # Initialize doctors (will use loaded state if resuming)
        self.doctors = self._init_doctors()

    def _load_simulation_state(self) -> bool:
        """Load the previous simulation state from the database.
        
        Returns:
            bool: True if state was successfully loaded, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Use dictionary-like rows
            cursor = conn.cursor()
            
            # Get the latest simulation state for this simulation ID
            state = cursor.execute(
                'SELECT * FROM sim_metadata WHERE sim_id = ? ORDER BY id DESC LIMIT 1', 
                (self.sim_id,)
            ).fetchone()
            
            if state:
                # Extract and set basic properties
                self.start_date = datetime.fromisoformat(state['start_date'])
                last_sim_time = float(state['last_sim_time'])
                self.patients_total = int(state['patients_total'])
                self.patients_treated = int(state['patients_treated'])
                
                # Set the environment's now time to continue from where we left off
                self.env.process(self._set_env_time(last_sim_time))
                
                # Restore doctor state (will be used in _init_doctors)
                self.doctor_state = json.loads(state['active_doctors'])
                
                print(f"Resumed simulation {self.sim_id} from {self.start_date.isoformat()}, time: {last_sim_time} minutes")
                print(f"State: {self.patients_total} total patients, {self.patients_treated} treated")
                
                conn.close()
                return True
            else:
                print(f"No previous simulation state found for simulation ID {self.sim_id}. Starting fresh.")
                conn.close()
                return False
        except Exception as e:
            print(f"Error loading simulation state: {e}")
            return False
            
    def _set_env_time(self, target_time: float):
        """Helper process to advance the environment time to the saved point.
        
        Args:
            target_time: Target simulation time in minutes
            
        Yields:
            simpy.Timeout: SimPy timeout event to advance simulation time
        """
        yield self.env.timeout(target_time)

    def _init_doctors(self) -> List[Doctor]:
        """Initialize doctors, potentially using loaded state.
        
        Returns:
            List[Doctor]: List of initialized doctors
        """
        doctors = []
        id_counter = 1
        
        # If we have a saved doctor state and we're resuming, use it
        if hasattr(self, 'doctor_state') and self.resume:
            for doc_data in self.doctor_state:
                doctor = Doctor(doc_data['id'], doc_data['specialty'], self.env)
                doctor.patients_treated = doc_data['patients_treated']
                doctors.append(doctor)
                id_counter = max(id_counter, doc_data['id'] + 1)
        else:
            # Regular initialization
            spec_counts = {s: max(1, int(self.num_doctors * SPECIALTY_PROPORTIONS[s])) for s in SPECIALTIES}
            # Adjust to reach total
            while sum(spec_counts.values()) < self.num_doctors:
                for s in ["generalist", "emergency"]:
                    if sum(spec_counts.values()) < self.num_doctors:
                        spec_counts[s] += 1
            for spec, count in spec_counts.items():
                for _ in range(count):
                    doctors.append(Doctor(id_counter, spec, self.env))
                    id_counter += 1
                    
        return doctors

    def get_seasonal_weights(self, sim_time: float) -> List[int]:
        """Calculate disease weights based on seasonal patterns.
        
        Modifies the base disease weights according to the current month to simulate
        seasonal variations in disease prevalence.
        
        Args:
            sim_time: Current simulation time in minutes
            
        Returns:
            List of weights for disease selection, higher values = higher probability
        """
        # Calculate current date from simulation time
        current_date = self.start_date + timedelta(minutes=sim_time)
        month = current_date.month - 1  # 0-based index
        
        # Base weights
        weights = DISEASE_WEIGHTS.copy()
        
        # Winter (Dec, Jan, Feb): more viral_infection, less asthma
        if month in [11, 0, 1]:
            weights[0] = int(DISEASE_WEIGHTS[0] * 1.7)  # viral_infection
            weights[3] = int(DISEASE_WEIGHTS[3] * 0.5)  # asthma_attack
        # Spring (Mar, Apr, May): more asthma, less viral
        elif month in [2, 3, 4]:
            weights[3] = int(DISEASE_WEIGHTS[3] * 2.0)  # asthma_attack
            weights[0] = int(DISEASE_WEIGHTS[0] * 0.7)  # viral_infection
        # Summer (Jun, Jul, Aug): more fractures, less viral
        elif month in [5, 6, 7]:
            weights[1] = int(DISEASE_WEIGHTS[1] * 1.5)  # minor_fracture
            weights[0] = int(DISEASE_WEIGHTS[0] * 0.5)  # viral_infection
        # Autumn (Sep, Oct, Nov): more gastroenteritis
        elif month in [8, 9, 10]:
            weights[8] = int(DISEASE_WEIGHTS[8] * 2.0)  # gastroenteritis
            
        # Apply the month factor to adjust overall disease probability
        month_factor = MONTH_FACTORS[month]
        if month_factor != 1.0:
            weights = [int(w * month_factor) for w in weights]
        
        # Normalize to avoid all zeros
        if sum(weights) == 0:
            weights = DISEASE_WEIGHTS.copy()
            
        return weights

    def get_time_of_day_factor(self, sim_time: float) -> float:
        """Returns a multiplier for patient arrival rate based on time of day.
        
        Provides hourly adjustment factors that make the simulation more realistic
        by having lower patient volumes at night and higher volumes during peak hours.
        
        Args:
            sim_time: Simulation time in minutes
            
        Returns:
            float: Multiplier for the base arrival rate
        """
        # Convert sim_time to hour of day (0-23)
        minutes_in_day = 24 * 60
        day_minute = sim_time % minutes_in_day
        hour = int(day_minute // 60)
        
        # Use the hour factors from config
        return HOUR_FACTORS[hour]

    def run(self, sim_minutes: int = 525600) -> None:
        """Run the hospital simulation for the specified duration.
        
        Args:
            sim_minutes: Duration to run the simulation in minutes (default: 1 year)
        """
        self.env.process(self.patient_arrivals())
        self.env.process(self.data_collector())
        self.env.run(until=sim_minutes)

    def patient_arrivals(self):
        """Generate patient arrivals and assign them to appropriate doctors.
        
        This process runs continuously, generating patients according to
        time-of-day patterns, weekday/weekend patterns, and seasonal variations.
        
        Yields:
            simpy.Timeout: Time until next patient arrival
        """
        while True:
            # Apply time-of-day factor from config
            time_factor = self.get_time_of_day_factor(self.env.now)
            
            # Apply day-of-week factor from config (0=Monday, 6=Sunday)
            day_of_week = int((self.env.now // (24 * 60)) % 7)
            day_factor = DAY_FACTORS[day_of_week]
            
            # Apply month factor from config (1=January, 12=December)
            current_date = self.start_date + timedelta(minutes=self.env.now)
            month_factor = MONTH_FACTORS[current_date.month - 1]  # Adjust for 0-based index
            
            # Check for special dates
            special_factor = 1.0
            for special_date in SPECIAL_DATES:
                if current_date.month == special_date["month"] and current_date.day == special_date["day"]:
                    special_factor = special_date["factor"]
                    break
            
            # Calculate effective arrival rate with all factors
            effective_rate = self.arrival_rate * time_factor * day_factor * month_factor * special_factor
            
            # Hospital might be on diversion if extremely busy (over 90% capacity)
            busy_doctors = sum(1 for d in self.doctors if d.resource.count > 0)
            busy_factor = 1.0
            if busy_doctors > 0.9 * len(self.doctors):
                busy_factor = 0.7  # Reduced arrivals during high occupancy
            
            # Adjust arrival time based on all factors
            adjusted_rate = max(1, effective_rate * busy_factor)  # Ensure at least 1/hour
            interarrival = np.random.exponential(60 / adjusted_rate)
            
            yield self.env.timeout(interarrival)
            
            # Get seasonal disease distribution
            seasonal_weights = self.get_seasonal_weights(self.env.now)
            disease, mean_time, specialty = random.choices(DISEASES, weights=seasonal_weights, k=1)[0]
            treatment_time = max(1, int(np.random.exponential(mean_time)))
            
            patient = Patient(
                id=f"P{self.patients_total}",
                disease=disease,
                treatment_time=treatment_time,
                specialty=specialty,
                arrival_time=self.env.now,
            )
            self.patients_total += 1
            self.env.process(self.handle_patient(patient))

    def handle_patient(self, patient: Patient):
        """Process a patient through the hospital system.
        
        This includes finding an appropriate doctor, waiting in queue if needed,
        treatment, and recording the outcome.
        
        Args:
            patient: Patient object to be treated
            
        Yields:
            simpy.events: SimPy event sequence for patient handling
        """
        # Find available doctor of required specialty
        candidates = [d for d in self.doctors if d.specialty == patient.specialty]
        if not candidates:
            candidates = [d for d in self.doctors if d.specialty == "generalist"]
        # Prefer free doctor, else shortest queue
        free_doctors = [d for d in candidates if d.resource.count == 0]
        if free_doctors:
            doctor = random.choice(free_doctors)
        else:
            doctor = min(candidates, key=lambda d: len(d.queue))
        doctor.queue.append(patient)
        with doctor.resource.request() as req:
            yield req
            doctor.queue.remove(patient)
            patient.start_treatment = self.env.now
            yield self.env.timeout(patient.treatment_time)
            patient.end_treatment = self.env.now
            doctor.patients_treated += 1
            self.patients_treated += 1
            self.save_patient_event(patient, doctor)

    def data_collector(self):
        """Periodically save simulation state and hospital metrics.
        
        This process runs every minute in simulation time, updating the database
        with current hospital status and occasionally saving the complete simulation
        state for possible resumption later.
        
        Yields:
            simpy.Timeout: One minute timeout between data collection points
        """
        while True:
            self.save_hospital_state()
            
            # Save simulation state every hour (60 minutes)
            if int(self.env.now) % 60 == 0 and self.env.now > 0:
                self.save_simulation_state()
                
            yield self.env.timeout(1)

    def save_patient_event(self, patient: Patient, doctor: Doctor) -> None:
        """Save a patient treatment event to the database.
        
        Args:
            patient: Patient object that was treated
            doctor: Doctor object that performed the treatment
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert simulation minutes to actual dates
            arrival_date = self.start_date + timedelta(minutes=patient.arrival_time)
            start_treatment_date = self.start_date + timedelta(minutes=patient.start_treatment)
            end_treatment_date = self.start_date + timedelta(minutes=patient.end_treatment)
            
            cursor.execute('''
            INSERT INTO patient_treated 
            (sim_id, doctor_id, doctor_specialty, disease, treatment_time, wait_time, 
            arrival_time, start_treatment, end_treatment, sim_minutes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.sim_id,
                doctor.id,
                doctor.specialty,
                patient.disease,
                patient.treatment_time,
                patient.start_treatment - patient.arrival_time,
                arrival_date.isoformat(),
                start_treatment_date.isoformat(),
                end_treatment_date.isoformat(),
                patient.end_treatment,  # Store original sim minutes too
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving patient data: {e}")

    def save_hospital_state(self) -> None:
        """Save the current hospital state to the database.
        
        Records metrics including patient counts, busy doctors, and waiting patients.
        Also stores the current simulation date and time.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            busy_doctors = sum(1 for d in self.doctors if d.resource.count > 0)
            waiting_patients = sum(len(d.queue) for d in self.doctors)
            
            # Convert simulation time to actual date
            current_sim_date = self.start_date + timedelta(minutes=self.env.now)
            
            cursor.execute('''
            INSERT INTO hospital_state 
            (sim_id, patients_total, patients_treated, busy_doctors, waiting_patients, sim_time, sim_minutes, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.sim_id,
                self.patients_total,
                self.patients_treated,
                busy_doctors,
                waiting_patients,
                current_sim_date.isoformat(),
                self.env.now,
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving hospital state: {e}")
            
    def save_simulation_state(self) -> None:
        """Save the current simulation state for later resuming.
        
        Stores essential information about the simulation including all doctor states,
        patient counts, and timing information to allow resuming the simulation later.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prepare serialized doctor state
            doctor_state = []
            for doctor in self.doctors:
                doctor_state.append({
                    'id': doctor.id,
                    'specialty': doctor.specialty,
                    'patients_treated': doctor.patients_treated,
                    'queue_length': len(doctor.queue),
                    'is_busy': doctor.resource.count > 0
                })
            
            # Save current state for this simulation ID
            cursor.execute('''
            INSERT INTO sim_metadata 
            (sim_id, start_date, last_sim_time, patients_total, patients_treated, active_doctors, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.sim_id,
                self.start_date.isoformat(),
                self.env.now,
                self.patients_total,
                self.patients_treated,
                json.dumps(doctor_state),
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
            print(f"Simulation state saved at minute {self.env.now}")
        except Exception as e:
            print(f"Error saving simulation state: {e}")