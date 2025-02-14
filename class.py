class Medecin:

    def __init__(self):
        self.patients = []
        self.en_charge = None

    def occupé(self):
        return self.en_charge is not None

class Patient:

    def __init__(self, arrival_time=0):
        self.arrival_time = arrival_time

class Hopital:

    def __init__(self, beds = 500, medecins = []):
        self.beds = beds
        self.file_attente = []
        self.medecins = medecins

class Maladie:
    def __init__(sefl,taux_mortalite, taux_contagion,temps_rémission):
        self.taux_mortalite = taux_mortalite
        self.taux_contagion = taux_contagion
        self.temps_rémission = temps_rémission

class World:
    # Monde à temps discret par jours
    def __init__(self, hopitaux = [], population = 1000):
        self.hopitaux = hopitaux
        self.population = population
        self.maladies = []