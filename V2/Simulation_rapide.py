"""
Created on Tue Mar 11 09:41:49 2025

@author: maxence
"""

import heapq
import numpy as np
from datetime import datetime, timedelta

# Paramètres
lambda_arrivee = 5  # taux moyen de nouveau patients par heure
mu_service = 2  # taux moyen patients traités par heure
n_medecins = 4  # Nombre de médecins disponibles
temps_total = 24  # Simulation sur 24 heures
heure_depart_simulation = datetime.strptime("08:00:00", "%H:%M:%S")  # Début de la journée


temps_arrivees = np.cumsum(np.random.exponential(1/lambda_arrivee, size=1000)) # Ariive de manière aléatoire des patients et size nombre maximum de patient en une journée
temps_arrivees = temps_arrivees[temps_arrivees < temps_total]  #Obtenir l'heure d'arrivé par rapoort au temps total de la simulation


temps_service = np.random.exponential(1/mu_service, len(temps_arrivees)) # Générer les temps de service

# File d’attente avec médecins disponibles
medecins_disponibles = [0] * n_medecins  # Liste des heures de disponibilité
file_attente = []

for i in range(len(temps_arrivees)):
    heure_arrivee = temps_arrivees[i]

    index_medecin = heapq.heappop(medecins_disponibles) # Trouver le médecin qui se libère en premier
    
    heure_debut_service = max(heure_arrivee, index_medecin) # Déterminer l’heure de début du service
    heure_fin_service = heure_debut_service + temps_service[i]
    
    heure_arrivee_dt = heure_depart_simulation + timedelta(hours=heure_arrivee) # Conversion en format datetime 
    heure_debut_service_dt = heure_depart_simulation + timedelta(hours=heure_debut_service)
    heure_fin_service_dt = heure_depart_simulation + timedelta(hours=heure_fin_service)

    file_attente.append((heure_arrivee_dt, heure_debut_service_dt, heure_fin_service_dt) # Stocke les résultats) 
    
    heapq.heappush(medecins_disponibles, heure_fin_service)  # Mettre à jour la disponibilité du médecin

print("\nSimulation des consultations avec plusieurs médecins :")
print("--------------------------------------------------------")
for i, (arrivee, debut, fin) in enumerate(file_attente):
    print(f"Patient {i+1}: Arrivée à {arrivee.strftime('%H:%M:%S')}, "
          f"Début consultation à {debut.strftime('%H:%M:%S')}, "
          f"Fin consultation à {fin.strftime('%H:%M:%S')}\n")

