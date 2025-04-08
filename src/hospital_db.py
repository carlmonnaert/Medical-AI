import database as db
import time as t

DB_PATH = "../data/hospital.db"

DISEASES = ["generic"]

TABLES = {
    "patients": [
        (1, "id", int),
        (0, "state", str),
        (0, "arrival", int),
        (0, "end", int),
        (0, "disease", str),
    ],
    "events": [
        (1, "id", int),
        (0, "state", str),
        (0, "start", int),
        (0, "duration", str),
        (2, "patient_id", ("patients", "id")),
    ],
    "doctors": [
        (1, "id", int),
        (0, "state", str),
        (0, "state", str),
        (2, "assigned_patient_id", ("patients", "id")),
    ],
}


class HospitalDb:
    """Class that will act as interface between the simulator and the database, to store
    the state of our simulations.
    """

    def __init__(self, db_path=DB_PATH):
        """Initiate the hospital manager:
        - db_path:"""
        self.manager = db.DatabaseManager(db_path)
        self.last_update = None

    def create_patient_table(self):
        """Create the patient table (if it doesn't exist yet)"""
        self.manager.create_table(
            "patients",
            TABLES["patients"]
        )

    def create_event_table(self):
        """Create the event table (if it doesn't exist yet)"""
        self.manager.create_table(
            "events",
            TABLES["events"]
        )

    def create_doctor_table(self):
        """Create the doctor table (if it doesn't exist yet)"""
        self.manager.create_table(
            "doctors",
            TABLES["doctors"]
        )

    def add_patient(self, state, arrival, disease):
        if disease not in DISEASES:
            print(
                f"ERROR - the specified disease ({disease}) is not supported, see documentation for more information."
            )
            return 1
        if disease is None:
            disease = "generic"
        self.manager.insert_value(
            "patients",
            ("id", "state", "arrival", "disease"),
            (id, state, arrival, disease),
        )

    def update_patient_state(self, patient_id):
        self.manager.udpate_value("patients", f"id = {patient_id}")

    def add_event(self, state, start, duration, patient_id):
        # TODO
        pass
