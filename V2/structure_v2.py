import numpy as np
from numpy import random as rd
import time

class Hopital:

    def __init__(self, dt : int = 5*60, files_attente=1, N_medecins=1, lambda_poisson=1, mu_exponetielle=1):
        """
        Classe qui représente un hôpital
        :param dt: durée d'un tour de boucle
        :param files_attente: nombre de files d'attente
        :param lambda_poisson: paramètre de la loi de Poisson qui génère les arrivées de patients
        """
        self.dt = dt
        self.files_attente = [ [] for k in range(files_attente) ]
        self.en_consultation = [None for k in range(N_medecins)]
        self.lambda_poisson = lambda_poisson #nombre de gens qui arrive par heure
        self.mu_exponetielle = mu_exponetielle #temps moyen du temps de traitement en minute
        self.prochaine_arrivee = 0
        self.soignés = 0

    def arrivee_patients(self):
        """
        Génère les arrivées de patients
        """
        if self.prochaine_arrivee <= 0:            
            
            prochaine_arrivee = np.random.poisson(self.lambda_poisson*self.dt)
            self.prochaine_arrivee = prochaine_arrivee

            temps_de_traitement = int(np.random.exponential(self.mu_exponetielle))
            nb_files = len(self.files_attente)
            patient = Personne(temps_de_traitement,self.dt)
            self.files_attente[rd.randint(0,nb_files)].append(patient)
        else:
            self.prochaine_arrivee -= self.dt

    def mise_a_jour_patients(self):
        """
        Met à jour l'état de l'hôpital
        """
        for file in self.files_attente:
            if len(file) > 0:
                file[-1].mise_a_jour()
            
        for k in range(len(self.files_attente)):
            avant = len(self.files_attente[k])
            self.files_attente[k] = [personne for personne in self.files_attente[k] if personne.temps_de_traitement > 0]
            apres = len(self.files_attente[k])
            self.soignés += avant-apres

    def suivant(self):
        """
        Passe au tour de boucle suivant
        """
        self.arrivee_patients()
        self.mise_a_jour_patients()

    def __str__(self):
        """
        Affiche l'état de l'hôpital
        """
        for k in range(len(self.files_attente)):
            print("total traité : ", self.soignés)
            print("File d'attente ", k+1, " : ", len(self.files_attente[k]), " personnes")

class Personne:
    """
    Classe qui représente une personne
    :param temps_de_traitement: temps de traitement de la personne
    :param statut: statut de la personne (False : en attente ou True : en traitement)
    """
    def __init__(self,temps_de_traitement : int,dt : int = 1):
        self.temps_de_traitement = temps_de_traitement
        self.dt = dt

    def mise_a_jour(self):
        self.temps_de_traitement -= self.dt
        if self.temps_de_traitement <= 0:
            print("Patient traité")

def run():
    h = Hopital(dt=60*5,files_attente = 1,lambda_poisson = 3, mu_exponetielle=3)
    compte = 0
    while True :
        print("\n\ntemps : ", h.dt*compte)
        h.suivant()
        h.__str__()
        compte += 1
        time.sleep(1)
run()