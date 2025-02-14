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
    def __init__(self,taux_mortalite, taux_contagion, taux_rémission,multiplicateur_hopital):
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
        self.en_attente = False
        self.en_traitement = False
        self.vivant = True

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
        Met à jour l'état de l'hopital en supposant que la population a déjà été mise à jour:
            - les personnes qui ne sont plus vivantes ou guéries sont retirées de la file d'attente et du traitement
            - les personnes en attente qui sont malades et pour qui il reste des lits sont mises en traitement
        """
        for personne in self.en_traitement:
            if not personne.vivant() or not personne.malade():
                self.en_traitement.remove(personne)

        for personne in self.file_attente:
            if not personne.vivant() or not personne.malade():
                self.file_attente.remove(personne)
            elif personne.malade() and self.lits_dispos > 0:
                self.en_traitement.append(personne)
                self.file_attente.remove(personne)
                self.lits_dispos -= 1

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
        nb_hopitaux = len(self.hopitaux)
        self.jour += 1

        for personne in self.population:
            personne.jour_suivant()
            
            if not personne.vivant:
                self.population.remove(personne)
            
            elif personne.malade() and not personne.en_traitement and not personne.en_attente:
                self.hopitaux[rd.randint(0,nb_hopitaux-1)].file_attente.append(personne)

        for hopital in self.hopitaux:
            hopital.jour_suivant()
        print("Jour",self.jour,"\n","Population:",len(self.population))


def create_world(population_n = N_population, hopitaux = N_hopitaux):
    """
    Crée un monde avec une population de population_n personnes et hopitaux hopitaux avec 5 medecins chacun
    """
    hopitaux = [Hopital(50,[Medecin() for k in range(5)]) for i in range(hopitaux)]
    maladies = [Maladie(0.1,0.2,0.1,1.5)]
    population = [ Personne(0) for k in range(population_n)]
    return World(hopitaux, population, maladies)

world = create_world()
for k in range(100):
    world.next_day()