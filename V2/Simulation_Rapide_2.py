import numpy as np
from numpy import random as rd
from datetime import datetime, timedelta
import time

class Hopital:

    def __init__(self, dt : int, files_attente=6, lambda_poisson=10, mu_exponetielle=3):
        """
        Classe qui représente un hôpital
        :param dt: durée d'un tour de boucle
        :param files_attente: nombre de files d'attente
        :param lambda_poisson: paramètre de la loi de Poisson qui génère les arrivées de patients
        """
        self.dt = dt
        self.files_attente = [ [] for k in range(files_attente) ] #Le nombre de file correspond aux nombres de médécins
        self.lambda_poisson = 1/lambda_poisson #nombre de gens qui arrive par heure
        self.mu_exponetielle = 1/mu_exponetielle #temps moyen du temps de traitement 
        self.prochaine_arrivee = 0
        self.soignés = 0
        self.occupé = 0 #Decrit si le patient est pris en charge ou non

    def arrivee_patients(self):
        """
        Génère les arrivées de patients
        """
        if self.prochaine_arrivee <= 0:         
            
            prochaine_arrivee = np.random.poisson(self.lambda_poisson*self.dt*60)
            self.prochaine_arrivee = prochaine_arrivee

            temps_de_traitement = int(np.random.exponential(self.mu_exponetielle*self.dt*60))
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
            if len(file)>0:
                file[0].mise_a_jour()
            
        for k in range(len(self.files_attente)):
            avant = len(self.files_attente[k])
            self.files_attente[k] = [personne for personne in self.files_attente[k] if personne.temps_de_traitement > 0]
            apres = len(self.files_attente[k])
            self.occupé = avant - apres
            #print("Patients en consulation    :", avant-apres)
            #print("Personnes traitées : ", avant-apres)
            self.soignés += avant-apres

    def suivant(self):
        """
        Passe au tour de boucle suivant
        """
        self.arrivee_patients()
        self.mise_a_jour_patients()

    def __str__(self):
        """
        Affiche l'état de l'hôpital (patients traités et files d'attente)
        """
        self.file_attente()
        self.en_consultation()
        self.nombre_total_traite()
        for k, file in enumerate(self.files_attente, start=1):
            #print(f"File d'attente {k} : {len(file)} personnes")
            break
            
    def nombre_total_traite(self): 
        """
        Affiche le nombre total de patients traités
        """
        print(f"Total Patients traités     : {self.soignés}")
        
    def file_attente(self,):
        """
        Affiche le nombre total de patients en file d'attente (toutes files confondues)
        """
        total_attente = sum(len(file) for file in self.files_attente)
        print(f"Patients en file d'attente : {total_attente}")
        
    def en_consultation(self):
        """
        Affiche le nombre de patient pris en consultation
        """
        if self.occupé == 0 :
            print("Patients en consulation    : Oui")
        else :
            print("Patients en consulation    : Non")
 


class Personne:
    """
    Classe qui représente une personne
    :param temps_de_traitement: temps de traitement de la personne
    :param statut: statut de la personne (False : en attente ou True : en traitement)
    """
    def __init__(self,temps_de_traitement : int,dt : int = 1):
        self.temps_de_traitement = temps_de_traitement
        print(temps_de_traitement)
        self.dt = dt

    def mise_a_jour(self):
        self.temps_de_traitement -= self.dt
        if self.temps_de_traitement <= 0:
            print("Patient traité")

def run():
    h = Hopital(1,3,20,8)
    compte = 0
    while True :
        print("\n\nHeure                      :",timedelta(minutes=h.dt*compte))
        h.suivant()
        h.__str__()
        compte += 1
        time.sleep(0.3)
run()