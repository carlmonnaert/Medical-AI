import sqlite3
import csv

DB_PATH = "./data/hospital.db"

# Global variable to hold the database connection
conn = None
cursor = None

def initialize_database():
    global conn, cursor
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables if they do not exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        disease TEXT,
        arrival_time INTEGER,
        waiting_time INTEGER,
        treatment_start_time INTEGER,
        treatment_end_time INTEGER,
        status TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        availability_status TEXT,
        treatment_start_time INTEGER,
        treatment_end_time INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS queue_stats (
        timestamp INTEGER,
        queue_length INTEGER,
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS overall_stats (
        total_patients_treated INTEGER,
        average_treatment_time REAL,
        doctors_available INTEGER,
        timestamp INTEGER
    )
    ''')

    # Commit the changes
    conn.commit()

# Function to insert patient data
def insert_patient(arrival_time, waiting_time, treatment_start_time, treatment_end_time, status):
    if cursor is not None:
        cursor.execute('''
        INSERT INTO patients arrival_time, waiting_time, treatment_start_time, treatment_end_time, status)
        VALUES (?, ?, ?, ?, ?)
        ''', (arrival_time, waiting_time, treatment_start_time, treatment_end_time, status))
    if conn is not None:
        conn.commit()

# Function to insert doctor data
def insert_doctor(doctor_id, availability_status, specialty, treatment_start_time, treatment_end_time):
    if cursor is not None:
        cursor.execute('''
        INSERT INTO doctors (availability_status, specialty, treatment_start_time, treatment_end_time)
        VALUES (?, ?, ?, ?)
        ''', (doctor_id, availability_status, specialty, treatment_start_time, treatment_end_time))
    if conn is not None:
        conn.commit()

# Function to insert queue stats
def insert_queue_stats(timestamp, queue_length, average_waiting_time, peak_waiting_time):
    if cursor is not None:
        cursor.execute('''
        INSERT INTO queue_stats (timestamp, queue_length, average_waiting_time, peak_waiting_time)
        VALUES (?, ?, ?, ?)
        ''', (timestamp, queue_length, average_waiting_time, peak_waiting_time))
    if conn is not None:
        conn.commit()

# Function to insert overall stats
def insert_overall_stats(total_patients_treated, average_treatment_time, doctors_available, timestamp):
    if cursor is not None:
        cursor.execute('''
        INSERT INTO overall_stats (total_patients_treated, average_treatment_time, doctors_available, timestamp)
        VALUES (?, ?, ?, ?)
        ''', (total_patients_treated, average_treatment_time, doctors_available, timestamp))
        if conn is not None:
            conn.commit()

# Function to export table data to CSV
def export_table_to_csv(table_name, file_name):
    if cursor is not None:
        cursor.execute(f'SELECT * FROM {table_name}')
        rows = cursor.fetchall()

        # Get column names
        column_names = [description[0] for description in cursor.description]

        # Write to CSV file
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(column_names)
            writer.writerows(rows)

# Close the connection when the module is imported
import atexit
atexit.register(lambda: conn.close() if conn else None)
