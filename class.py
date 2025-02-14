import random as rd

N_hopitaux = 10
N_population = 1000


class Medecin:
    def __init__(self):
        self.en_charge = None

    def occupé(self):
        return self.en_charge is not None

class Maladie:
    """
    Classe qui représente une maladie: - taux de mortalité (% de chance de mourrir chaque jour)
                                       - taux de contagion (% de chance qu'une personne tombe malade)
                                       - taux de rémission (% de chance qu'une personne guérisse d'elle même chaque jour)
                                       - un multiplicateur qui augmente le taux de rémission/diminue la mortalité quand le patient est à l'hopital
    """
    def __init__(sefl,taux_mortalite, taux_contagion, taux_rémission,multiplicateur_hopital):
        self.taux_mortalite = taux_mortalite
        self.taux_contagion = taux_contagion
        self.taux_rémission = taux_rémission

class Personne:
    """
    Classe qui représente une personne : - date d'arrivée à l'hopital
                                         - le type de maladie (si elle est malade)
                                         - son état (vivant ou mort)
    """
    def __init__(self, arrival_time=0, malade = False,maladie = None):
        self.arrival_time = arrival_time
        self.maladie = maladie
        self.waiting = False
        self.en_traitement = False
        self.vivant = True
        self.hoptital = 

    def malade(self):
        return self.maladie is not None

    def mourir(self):
        self.vivant = False

    def guerir(self):
        self.arrival_time = 0
        self.maladie = None
        self.en_traitement = False
        self.waiting = False

    def jour_suivant(self):
        """
        Met à jour l'état de la personne en fonction de sa maladie
        """
        if self.malade():

            multiplicateur = self.maladie.multiplicateur_hopital if self.en_traitement else 1
            
            if self.maladie.taux_mortalite/multiplicateur > rd.random():
                self.mourir()
            
            elif self.maladie.taux_rémission > rd.random():
                self.guerir()
            

class Hopital:
    """
    Classe qui réprésente un hopital : - un ensemble de lits
                                       - un ensemble de medecins
                                       - un ensemble de patients (en attente ou en traitement)
                                       - un nombre de lits disponibles
    """
    def __init__(self, lits = 500, medecins = []):
        self.file_attente = []
        self.en_traitement = []
        self.lits_dispos = lits
        self.medecins = medecins

    def jour_suivant(self):
        """
        Met à jour l'état de l'hopital en supposant que la population a déjà été mise à jour
        """
        en_traitement_1 = []
        file_attente_1 = []

        for personne in self.traitement:
            if personne.malade() and personne.vivant():
                en_traitement_1.append(personne)
        
        for personne in self.file_attente:
            if personne.malade() and personne.vivant():
                file_attente_1.append(personne)
        
        self.en_traitement = en_traitement_1
        self.file_attente = file_attente_1

class World:
    """
    Classe qui représente le monde dans lequel on évolue: - un ensemble d'hopitaux
                                                          - une population
                                                          - un ensemble de maladies
                                                          - la date actuelle
    """
    def __init__(self, hopitaux = [], population = [], maladies =[]):
        self.hopitaux = hopitaux
        self.population = population
        self.maladies = maladies
        self.jour = 0

    def next_day(self):
        
        for personne in self.population:
            personne.jour_suivant()
        
        for hoptital in self.hopitaux:
            hopital.jour_suivant()

def create_world(population_n = N_population, hopitaux = N_hopitaux):
    """
    Crée un monde avec une population de population_n personnes et hopitaux hopitaux avec 5 medecins chacun
    """
    hopitaux = [Hopital(50,[Medecin() for k in range(5)]) for i in range(hopitaux)]
    maladies = [Maladie(0.01,0.5,14)]
    population = [ Personne(0) for k in range(population_n)]
    return World(hopitaux, population, maladies)