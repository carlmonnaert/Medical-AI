import numpy as np
from numpy import random as rd


class Hopital:

    def __init__(self, dt : int, files_attente=1, lambda_poisson=1, mu_exponetielle=1):
        """
        Classe qui représente un hôpital
        :param dt: durée d'un tour de boucle
        :param files_attente: nombre de files d'attente
        :param lambda_poisson: paramètre de la loi de Poisson qui génère les arrivées de patients
        """
        self.dt = dt
        self.files_attente = [ [] for k in range(files_attente) ]
        self.lambda_poisson = lambda_poisson
        self.mu_exponetielle = mu_exponetielle

    def arrivee_patients(self):
        """
        Génère les arrivées de patients
        """
        nb_arrivees = np.random.poisson(self.lambda_poisson * self.dt)
        for k in range(nb_arrivees):
            nb_files = len(self.files_attente)
            temps_de_traitement = np.random.exponential(self.mu_exponetielle)
            self.files_attente[k % nb_files].append(Personne(temps_de_traitement,False,self.dt))


    def mise_a_jour_patients(self):
        """
        Met à jour l'état de l'hôpital
        """
        for file in self.files_attente:
            for personne in file:
                personne.mise_a_jour()
            
        for file in self.files_attente:
            file = [personne for personne in file if personne.temps_de_traitement > 0]

class Personne:
    """
    Classe qui représente une personne
    :param temps_de_traitement: temps de traitement de la personne
    :param statut: statut de la personne (False : en attente ou True : en traitement)
    """
    def __init__(self,temps_de_traitement : int, statut : bool = False,dt : int = 1):
        self.temps_de_traitement = temps_de_traitement
        self.statut = statut
        self.dt = dt

    def mise_a_jour(self):
        if self.statut:
            self.temps_de_traitement -= self.dt
