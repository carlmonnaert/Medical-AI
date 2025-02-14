class Medecin:
    def __init__(self):
        self.en_charge = None

    def occupé(self):
        return self.en_charge is not None

class Maladie:
    
    def __init__(sefl,taux_mortalite, taux_contagion, temps_rémission):
        self.taux_mortalite = taux_mortalite
        self.taux_contagion = taux_contagion
        self.temps_rémission = temps_rémission

class Personne:

    def __init__(self, arrival_time=0, malade = False,maladie = None):
        self.arrival_time = arrival_time
        self.malade = malade
        self.maladie = maladie
        self.waiting = False
        self.en_traitement = False

class Hopital:

    def __init__(self, lits = 500, medecins = []):
        self.file_attente = []
        self.en_traitement = []
        self.lits = lits
        self.medecins = medecins

class World:
    # Monde à temps discret par jours
    def __init__(self, hopitaux = [], population = [], maladies =[]):
        self.hopitaux = hopitaux
        self.population = population
        self.maladies = maladies
        self.jour = 0

def create_world(population_n = 1000, hopitaux = 10):

    hopitaux = [Hopital(50,[Medecin() for k in range(5)]) for i in range(hopitaux)]
    maladies = [Maladie(0.01,0.5,14)]
    population = [ Personne(0) for k in range(population_n)]
    return World(hopitaux, population, maladies)