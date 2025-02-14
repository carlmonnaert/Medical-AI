class Medecin:
    
    def __init__(self):
        self.patients = []
        self.en_charge = None

    def occupé(self):
        return self.en_charge is not None

class Patient:

    def __init__(self, arrival_time):


class Hopital:

    def __init__(self, beds = 500):
        self.beds = beds
        self.file = 