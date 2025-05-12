#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 11:18:35 2025

@author: maxence
"""

import numpy as np
from numpy import random as rd
from datetime import datetime, timedelta
import time
import sys, os, csv
import random


# Liste des maladies avec leur temps de traitement, spécialiste requis et facteurs saisonniers
# Format: [nom_maladie, temps_traitement, specialite, [facteur_hiver, facteur_printemps, facteur_ete, facteur_automne]]
Maladies = [
    ["infection_virale", 20, "generaliste", [1.8, 1.5, 1.2, 1.0, 0.8, 0.7, 0.6, 0.7, 0.9, 1.1, 1.3, 1.6]],
    ["fracture_legere", 50, "urgentiste", [1.3, 1.2, 1.0, 0.9, 0.8, 1.0, 1.3, 1.4, 1.2, 1.0, 1.1, 1.2]],
    ["plaie_ouverte", 30, "urgentiste", [0.9, 0.9, 0.9, 1.0, 1.1, 1.3, 1.5, 1.4, 1.2, 1.1, 1.0, 0.9]],
    ["crise_asthme", 45, "pneumologue", [1.2, 1.3, 1.5, 1.6, 1.4, 1.0, 0.8, 0.7, 1.0, 1.2, 1.3, 1.2]],
    ["douleurs_abdominales", 60, "generaliste", [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]],
    ["mal_dos_aigu", 30, "generaliste", [1.2, 1.1, 1.0, 0.9, 0.9, 0.9, 1.0, 1.0, 1.0, 1.1, 1.1, 1.2]],
    ["infection_urinaire", 15, "generaliste", [1.0, 1.0, 0.9, 0.9, 1.0, 1.1, 1.2, 1.3, 1.1, 1.0, 1.0, 1.0]],
    ["malaise", 40, "cardiologue", [1.3, 1.2, 1.1, 1.0, 0.9, 0.9, 1.0, 1.1, 1.0, 1.0, 1.1, 1.2]],
    ["gastro-enterite", 40, "generaliste", [2.8, 2.5, 1.8, 1.2, 0.8, 0.6, 0.5, 0.5, 0.7, 1.2, 1.8, 2.5]],
    ["femme_enceinte", 200, "gynecologue", [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]],
    ["avc", 400, "neurologue", [1.2, 1.1, 1.0, 0.9, 0.8, 0.8, 0.8, 0.8, 0.9, 1.0, 1.1, 1.2]],
    ["infarctus", 300, "cardiologue", [1.4, 1.3, 1.2, 1.0, 0.9, 0.8, 0.9, 0.9, 1.0, 1.1, 1.2, 1.3]],
    ["grippe", 25, "generaliste", [3.5, 3.2, 2.5, 1.5, 0.8, 0.5, 0.3, 0.3, 0.6, 1.2, 2.0, 3.0]],
    ["pneumonie", 70, "pneumologue", [2.8, 2.5, 2.0, 1.5, 1.0, 0.6, 0.5, 0.5, 0.8, 1.4, 2.0, 2.5]],
    ["allergie_saisonniere", 20, "generaliste", [0.3, 0.4, 1.5, 2.8, 3.0, 2.5, 1.5, 1.0, 0.8, 0.6, 0.4, 0.3]],
    ["intoxication_alimentaire", 35, "generaliste", [0.7, 0.7, 0.8, 0.8, 1.0, 1.5, 2.0, 2.0, 1.5, 1.0, 0.8, 0.7]],
    ["covid", 40, "pneumologue", [1.6, 1.5, 1.3, 1.2, 1.0, 0.8, 0.7, 0.8, 1.0, 1.2, 1.4, 1.5]],
    ["migraine", 15, "neurologue", [1.0, 1.1, 1.2, 1.3, 1.3, 1.0, 0.8, 0.8, 0.9, 1.0, 1.0, 1.0]],
    ["entorse", 40, "urgentiste", [0.8, 0.8, 0.9, 1.0, 1.2, 1.5, 1.8, 1.7, 1.4, 1.2, 1.0, 0.9]],
    ["brulure", 35, "urgentiste", [0.8, 0.8, 0.8, 0.9, 1.0, 1.5, 2.0, 2.0, 1.5, 1.0, 0.9, 0.8]],
    ["angine", 25, "generaliste", [1.5, 1.4, 1.2, 1.0, 0.8, 0.7, 0.6, 0.7, 0.9, 1.1, 1.3, 1.5]],
    ["sinusite", 20, "generaliste", [1.4, 1.3, 1.2, 1.1, 1.0, 0.8, 0.7, 0.8, 0.9, 1.0, 1.2, 1.3]],
    ["tachycardie", 100, "cardiologue", [1.1, 1.1, 1.0, 1.0, 0.9, 0.9, 0.9, 0.9, 1.0, 1.0, 1.1, 1.1]],
    ["epilepsie", 250, "neurologue", [1.0, 1.0, 1.1, 1.2, 1.1, 1.0, 0.9, 0.9, 1.0, 1.0, 1.0, 1.0]],
    ["bronchite", 60, "pneumologue", [2.0, 1.8, 1.5, 1.3, 1.0, 0.7, 0.6, 0.6, 0.8, 1.2, 1.5, 1.8]],
    ["torsion_cheville", 45, "urgentiste", [0.9, 0.9, 1.0, 1.0, 1.2, 1.4, 1.6, 1.5, 1.3, 1.1, 1.0, 0.9]]
]

# Poids de probabilité de base pour chaque maladie (sera ajusté selon la saison)
Poids_Base = [27, 20, 10, 6, 7, 6, 5, 5, 3, 3, 2, 1, 15, 8, 10, 7, 12, 8, 11, 9, 9, 7, 4, 4, 2, 7]


class Medecin:
    """
    Classe représentant un médecin
    :param id: Pour différencier les médecins
    :param specialité : pour sa spécialité
    :param patitent_traité : donné perso sur le nombre de patients traités pour ce médecin
    :param occupe : son staut pour savoir s'il est en consultation (True : il est avec un patient)
    :param file_attente : Ce sont les patiens qui attendent dans la file d'attente de ce médecin en particulier'
    """

    def __init__(self, identifiant, specialite):
        self.id = identifiant
        self.specialite = specialite
        self.patients_traites = 0
        self.occupe = False
        self.file_attente = []

    def __str__(self):
        """
        Affiche l'état du médecin
        """
        statut = "Occupé" if self.occupe else "Libre"
        return f"{self.specialite} {self.id:<3}\t{statut:<10}{len(self.file_attente):<20}{self.patients_traites}"


class Personne:
    """
    Classe qui représente une personne/patient
    :param temps_de_traitement: temps de traitement de la personne (assoyiez à la maladie qui va avoir)
    :param statut: statut de la personne (False : en attente ou True : en traitement)
    :param specialité_requise : la spécialité requise du médécin pour le soigner
    """

    def __init__(
        self, temps_de_traitement: int, dt: int = 1, maladie="", specialite=""
    ):
        self.temps_de_traitement = temps_de_traitement
        self.dt = dt
        self.maladie = maladie
        self.specialite_requise = specialite
        self.heure_arrivee = datetime.now()

    def mise_a_jour(self):
        self.temps_de_traitement -= self.dt


class Hopital:
    def __init__(self, dt: int, nb_medecin=6, lambda_poisson=10):
        """
        Classe qui représente un hôpital
        :param dt: durée d'un tour de boucle (1 minute)
        :param nb_medecin : nombre de médecins
        :param lambda_poisson: paramètre de la loi de Poisson qui génère les arrivées de patients (nombre de gens moyen qui arrive par heure)
        """
        self.dt = dt
        self.nb_medecins = nb_medecin

        # Initialisation des médecins avec leurs spécialités
        id_counter = 1
        self.medecins_par_specialite = {}

        # Création des médecins par spécialité avec les proportions souhaitées
        specialites = {
            "generaliste": int(0.321 * nb_medecin),#
            "urgentiste": int(0.215 * nb_medecin),
            "pneumologue": int(0.202 * nb_medecin),
            "neurologue": int(0.172 * nb_medecin),
            "cardiologue": int(0.093 * nb_medecin),
            "gynecologue": int(0.067 * nb_medecin)
        }

        # Ajuster pour s'assurer qu'il y a au moins un médecin de chaque spécialité
        for specialite in specialites:
            if specialites[specialite] == 0:
                specialites[specialite] = 1

        self.medecins = []  # Créer les médecins et les regrouper par spécialité
        for specialite, nombre in specialites.items():
            spec_medecins = [Medecin(id_counter + i, specialite) for i in range(nombre)]
            self.medecins_par_specialite[specialite] = spec_medecins
            self.medecins.extend(spec_medecins)
            id_counter += nombre

        while (
            len(self.medecins) < nb_medecin
        ):  # Ajouter des médecins urgentiste ou généraliste si nécessaire pour atteindre le bon nombre de médecin
            """aléatoire = random.randrange(0, 2)
            if aléatoire == 1:
                self.medecins.append(Medecin(id_counter, "generaliste"))
                self.medecins_par_specialite["generaliste"].append(self.medecins[-1])
                id_counter += 1
            else:"""
            self.medecins.append(Medecin(id_counter, "urgentiste"))
            self.medecins_par_specialite["urgentiste"].append(self.medecins[-1])
            id_counter += 1

        self.files_attente = [
            medecin.file_attente for medecin in self.medecins
        ]  # Référence aux files des médecins
        self.lambda_poisson = (
            lambda_poisson  # nombre de gens qui arrive en moyenne par heure
        )
        self.mu_exponetielle = 0  # temps moyen du temps de traitement : 0 par défaut
        self.prochaine_arrivee = 0
        self.soignés = 0
        self.temps_total = 0
        self.patients_totaux = 0
        
        # Variables pour la simulation jour par jour
        self.jour_actuel = 1
        self.heure_actuelle = 0
        self.date_debut = datetime(2025, 1, 1)  # Date de début de la simulation
        self.date_actuelle = self.date_debut
        
        # Statistiques par jour et par maladie
        self.stats_jour = {}
        self.stats_maladie = {maladie[0]: 0 for maladie in Maladies}
        self.stats_traitements_jour = {}
        
        # Créer les répertoires pour les données
        if not os.path.exists("./data"):
            os.makedirs("./data")
            
        # Initialiser les fichiers CSV
        self.initialiser_csv()
        
    def date_exacte(self):
        jours_semaine = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        mois_noms = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        
        date = self.date_actuelle
        mois_str = mois_noms[date.month - 1]
        
        return f"{date.day} {mois_str} {date.year}"    
                
    def determiner_mois_index(self, date):
        """
        Détermine l'index du mois (0 pour janvier, 1 pour février, etc.)
        """
        return date.month - 1  # 0-based index (0 = janvier, 11 = décembre)

    def ajuster_poids_saison(self):
        """
        Ajuste les poids des maladies en fonction du mois actuel
        """
        mois_index = self.determiner_mois_index(self.date_actuelle)
        poids_ajustes = []
        
        for i, maladie in enumerate(Maladies):
            facteur_mois = maladie[3][mois_index]
            poids_ajustes.append(Poids_Base[i] * facteur_mois)
            
        return poids_ajustes
            

    def arrivee_patients(self):
        """
        Génère les arrivées de patients et les attribue aux médecins appropriés selon leur spécialité
        """
        if self.prochaine_arrivee <= 0:
            # Nombre de minutes avant la prochaine arrivée (loi de Poisson)
            self.prochaine_arrivee = np.random.exponential(60 / self.lambda_poisson)

            # Ajuster les poids en fonction de la saison
            poids_saison = self.ajuster_poids_saison()

            # Choix pondéré d'une des maladies
            choix = random.choices(Maladies, weights=poids_saison, k=1)[0]
            maladie, temps_moyen, specialite_requise, _ = choix

            # Temps de traitement selon une loi exponentielle avec le temps moyen de la maladie
            temps_de_traitement = max(1, int(np.random.exponential(temps_moyen)))

            # Création du patient
            patient = Personne(
                temps_de_traitement, self.dt, maladie, specialite_requise
            )
            
            # Enregistrement des statistiques
            id_patient = f"P{self.patients_totaux}"
            self.stats_maladie[maladie] += 1
            
            jour_str = self.date_actuelle.strftime("%Y-%m-%d")
            if jour_str not in self.stats_jour:
                self.stats_jour[jour_str] = {maladie: 1}
            else:
                if maladie in self.stats_jour[jour_str]:
                    self.stats_jour[jour_str][maladie] += 1
                else:
                    self.stats_jour[jour_str][maladie] = 1
            
            self.patients_totaux += 1

            # Attribution du patient à un médecin de la bonne spécialité
            if specialite_requise in self.medecins_par_specialite:
                medecins_specialistes = self.medecins_par_specialite[specialite_requise]

                # Chercher un médecin libre de la bonne spécialité
                medecins_libres = [m for m in medecins_specialistes if not m.occupe]

                if medecins_libres:
                    # Attribuer au médecin libre
                    medecin_choisi = rd.choice(medecins_libres)
                else:
                    # Attribuer au médecin avec la file d'attente la plus courte
                    index_file_min = np.argmin(
                        [len(m.file_attente) for m in medecins_specialistes]
                    )
                    medecin_choisi = medecins_specialistes[index_file_min]
            else:
                # Si la spécialité n'existe pas (cas improbable), attribuer à un généraliste
                medecin_choisi = rd.choice(self.medecins_par_specialite["generaliste"])

            medecin_choisi.file_attente.append(patient)
        else:
            self.prochaine_arrivee -= self.dt

    def mise_a_jour_patients(self):
        """
        Met à jour l'état de l'hôpital et des médecins
        """
        # Suivi des maladies traitées par jour
        jour_str = self.date_actuelle.strftime("%Y-%m-%d")
        if jour_str not in self.stats_traitements_jour:
            self.stats_traitements_jour[jour_str] = {maladie[0]: 0 for maladie in Maladies}
        
        for medecin in self.medecins:
            if len(medecin.file_attente) > 0:
                medecin.occupe = True
                medecin.file_attente[0].mise_a_jour()
            else:
                medecin.occupe = False

            # Compter les patients traités
            avant = len(medecin.file_attente)
            traites = []
            
            # Collecter les patients traités pour les statistiques
            if medecin.occupe and medecin.file_attente:
                if medecin.file_attente[0].temps_de_traitement <= 0:
                    traites.append(medecin.file_attente[0])
            
            # Filtrer les patients encore en traitement
            medecin.file_attente = [
                personne
                for personne in medecin.file_attente
                if personne.temps_de_traitement > 0
            ]
            
            apres = len(medecin.file_attente)
            patients_traites = avant - apres
            
            # Mettre à jour les statistiques de traitement par maladie
            for patient in traites:
                self.stats_traitements_jour[jour_str][patient.maladie] += 1
            
            medecin.patients_traites += patients_traites
            self.soignés += patients_traites

    def initialiser_csv(self):
        """
        Initialise les fichiers CSV pour stocker les données
        """
        # Fichier pour les données quotidiennes de l'hôpital
        with open("./data/hospital_daily.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "patients_arrives", "patients_traites", "patients_en_attente", "medecins_occupes"])
        
        # Fichier pour les données des maladies par jour
        with open("./data/maladies_par_jour.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            entetes = ["date"] + [maladie[0] for maladie in Maladies]
            writer.writerow(entetes)
        
        # Fichier pour les traitements par jour et par maladie
        with open("./data/traitements_par_jour.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            entetes = ["date"] + [maladie[0] for maladie in Maladies]
            writer.writerow(entetes)
        
        # Fichier pour les données horaires détaillées
        with open("./data/data_horaire.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            entetes = [
                "date", "heure", "patients_arrives", "patients_traites", 
                "patients_en_attente", "medecins_occupes"
            ] + [f"file_attente_{m.specialite}_{m.id}" for m in self.medecins]
            writer.writerow(entetes)
        
        # Fichier pour les données mensuelles
        with open("./data/stats_mensuelles.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            entetes = ["annee", "mois"] + [maladie[0] for maladie in Maladies]
            writer.writerow(entetes)

    def sauvegarder_data_horaire(self):
        """
        Sauvegarde les données horaires de l'hôpital
        """
        nom_fichier = "./data/data_horaire.csv"
        
        date_str = self.date_actuelle.strftime("%Y-%m-%d")
        heure_str = f"{self.heure_actuelle:02d}:00"
        
        ligne = [
            date_str,
            heure_str,
            self.patients_totaux,
            self.soignés,
            sum(len(m.file_attente) for m in self.medecins),
            sum(1 for m in self.medecins if m.occupe),
        ] + [len(m.file_attente) for m in self.medecins]

        with open(nom_fichier, mode="a", newline="") as fichier_csv:
            writer = csv.writer(fichier_csv)
            writer.writerow(ligne)

    def sauvegarder_data_journaliere(self):
        """
        Sauvegarde les données journalières dans les fichiers CSV
        """
        jour_str = self.date_actuelle.strftime("%Y-%m-%d")
        
        # Données générales de l'hôpital par jour
        with open("./data/hospital_daily.csv", mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                jour_str, 
                self.patients_totaux, 
                self.soignés, 
                sum(len(m.file_attente) for m in self.medecins),
                sum(1 for m in self.medecins if m.occupe)
            ])
        
        # Données des maladies par jour
        with open("./data/maladies_par_jour.csv", mode="a", newline="") as f:
            writer = csv.writer(f)
            if jour_str in self.stats_jour:
                ligne = [jour_str]
                for maladie in [m[0] for m in Maladies]:
                    ligne.append(self.stats_jour[jour_str].get(maladie, 0))
                writer.writerow(ligne)
            else:
                ligne = [jour_str] + [0] * len(Maladies)
                writer.writerow(ligne)
        
        # Données des traitements par jour et par maladie
        with open("./data/traitements_par_jour.csv", mode="a", newline="") as f:
            writer = csv.writer(f)
            if jour_str in self.stats_traitements_jour:
                ligne = [jour_str]
                for maladie in [m[0] for m in Maladies]:
                    ligne.append(self.stats_traitements_jour[jour_str].get(maladie, 0))
                writer.writerow(ligne)
            else:
                ligne = [jour_str] + [0] * len(Maladies)
                writer.writerow(ligne)
    
    def sauvegarder_data_mensuelle(self):
        """
        Sauvegarde les données mensuelles dans un fichier CSV
        """
        # Créer un fichier pour les données mensuelles s'il n'existe pas
        if not os.path.exists("./data/stats_mensuelles.csv"):
            with open("./data/stats_mensuelles.csv", mode="w", newline="") as f:
                writer = csv.writer(f)
                entetes = ["annee", "mois"] + [maladie[0] for maladie in Maladies]
                writer.writerow(entetes)
        
        # Agréger les données par mois
        mois_courant = self.date_actuelle.month
        annee_courante = self.date_actuelle.year
        
        # Calculer les totaux par maladie pour le mois courant
        totaux_maladie = {maladie[0]: 0 for maladie in Maladies}
        
        for jour_str, stats in self.stats_jour.items():
            jour_date = datetime.strptime(jour_str, "%Y-%m-%d")
            if jour_date.month == mois_courant and jour_date.year == annee_courante:
                for maladie, count in stats.items():
                    if maladie in totaux_maladie:
                        totaux_maladie[maladie] += count
        
        # Enregistrer les données mensuelles
        with open("./data/stats_mensuelles.csv", mode="a", newline="") as f:
            writer = csv.writer(f)
            ligne = [annee_courante, mois_courant]
            for maladie in [m[0] for m in Maladies]:
                ligne.append(totaux_maladie.get(maladie, 0))
        writer.writerow(ligne)


    def suivant_minute(self):
        """
        Simule une minute
        """
        self.arrivee_patients()
        self.mise_a_jour_patients()
        self.temps_total += self.dt

    def suivant_heure(self):
        """
        Simule une heure (60 minutes)
        """
        for _ in range(60):
            self.suivant_minute()
        
        # Enregistre les données après chaque heure
        self.sauvegarder_data_horaire()
        
        # Mise à jour de l'heure
        self.heure_actuelle += 1
        if self.heure_actuelle >= 24:
            self.heure_actuelle = 0
            self.suivant_jour()

    def suivant_jour(self):
        """
        Passe au jour suivant et enregistre les données
        """
        # Sauvegarde des données du jour
        self.sauvegarder_data_journaliere()
        
        # Mise à jour de la date
        self.jour_actuel += 1
        self.date_actuelle = self.date_debut + timedelta(days=self.jour_actuel-1)
        
        # Affichage du changement de jour
        print(f"\n\n{'='*60}")
        print(f"NOUVEAU JOUR: {self.date_actuelle.strftime('%Y-%m-%d')} (Jour {self.jour_actuel})")
        mois = ["JANVIER", "FÉVRIER", "MARS", "AVRIL", "MAI", "JUIN", 
                "JUILLET", "AOÛT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DÉCEMBRE"]
        mois_actuel = mois[self.determiner_mois_index(self.date_actuelle)]
        print(f"MOIS: {mois_actuel}")
        print(f"{'='*60}\n")
            
    def __str__(self):
        """
        Affiche l'état de l'hôpital (patients traités et files d'attente)
        """
        self.file_attente()
        self.en_consultation()
        self.nombre_total_traite()
    
        # Afficher l'état de chaque médecin sous forme de tableau
        print("\nÉtat des médecins:")
        header = f"{'MÉDECIN':<20}{'STATUT':<10}{'PATIENTS EN ATTENTE':^22}{'PATIENTS TRAITÉS':^20}"
        print("-" * (len(header) + 4))
        print(header)
        print("-" * (len(header) + 4))
    
        # Afficher les médecins regroupés par spécialité
        for specialite in self.medecins_par_specialite:
            for medecin in self.medecins_par_specialite[specialite]:
                statut = "Occupé" if medecin.occupe else "Libre"
                nb_en_attente = len(medecin.file_attente)
                if statut == "Occupé" and nb_en_attente > 0:
                    nb_en_attente -= 1  # Si la médecin est occupé la file d'attente affiche 0 au lieu de 1
                ligne = f"{medecin.specialite + ' '}\t{(statut).center(20)}{str(nb_en_attente).center(20)}{str(medecin.patients_traites).center(22)}"
                print(ligne)
            print("\n")
        return ""

    def nombre_total_traite(self):
        """
        Affiche le nombre total de patients traités
        """
        print(f"Total Patients traités     : {self.soignés}")

    def file_attente(self):
        """
        Affiche le nombre total de patients en file d'attente (toutes files confondues)
        """
        total_attente = sum(len(medecin.file_attente) for medecin in self.medecins)
        print(f"Patients en file d'attente : {total_attente}")

    def en_consultation(self):
        """
        Affiche le nombre de médecins en consultation
        """
        nb_occupes = sum(1 for medecin in self.medecins if medecin.occupe)
        print(f"Médecins en consultation   : {nb_occupes}/{self.nb_medecins}")

    def afficher_bilan_final(self, sig=None, frame=None):
        """
        Affiche un bilan complet de la simulation à la fin
        """
        
        print("\n" + "=" * 50)
        print("BILAN FINAL DE LA SIMULATION")
        print("=" * 50)
        print(f"Date de début: {self.date_debut.strftime('%Y-%m-%d')}")
        print(f"Date de fin: {self.date_actuelle.strftime('%Y-%m-%d')}")
        print(f"Nombre de jours simulés: {self.jour_actuel}")
        print(f"Temps simulé: {timedelta(minutes=self.temps_total)}")
        print(f"Nombre total de patients arrivés: {self.patients_totaux}")
        print(f"Nombre total de patients traités: {self.soignés}")
    
        print("\nStatistiques par spécialité:\n")
        for specialite in self.medecins_par_specialite:
            total_spec = sum(
                m.patients_traites for m in self.medecins_par_specialite[specialite]
            )
            nb_medecins = len(self.medecins_par_specialite[specialite])
            print(
                f"  {specialite:<15} : {total_spec:} patients traités ({nb_medecins} médecins)"
            )
        
        print("\nStatistiques par maladie:\n")
        for maladie, nombre in sorted(self.stats_maladie.items(), key=lambda x: x[1], reverse=True):
            if nombre > 0:
                pourcentage = (nombre / self.patients_totaux * 100) if self.patients_totaux > 0 else 0
                print(f"  {maladie:<20} : {nombre:} patients ({pourcentage:.2f}%)")
    
        print("\nEfficacité du système:")
        if self.temps_total > 0:
            patients_par_heure = (self.soignés * 60) / self.temps_total
            print(f"  Moyenne de patients traités par heure: {patients_par_heure:.2f}")
            patients_par_jour = patients_par_heure * 24
            print(f"  Moyenne de patients traités par jour: {patients_par_jour:.2f}")
    
        taux_traitement = (
            (self.soignés / self.patients_totaux * 100)
            if self.patients_totaux > 0
            else 0
        )
        print(f"  Taux de traitement: {taux_traitement:.2f}%")
    
        print("\nFichiers CSV générés:")
        print("  - ./data/hospital_daily.csv (statistiques journalières)")
        print("  - ./data/maladies_par_jour.csv (maladies par jour)")
        print("  - ./data/traitements_par_jour.csv (traitements par jour)")
        print("  - ./data/data_horaire.csv (données détaillées par heure)")
        print("  - ./data/stats_mensuelles.csv (statistiques mensuelles)")
        
        print("=" * 50)
    
        # Quitter proprement le programme
        sys.exit(0)


def run(nb_jours=30):
    """
    Lance la simulation pour un nombre donné de jours
    """
    h = Hopital(
        1, 14, 24
    )  # dt = 1 minute ; nombre de médecins = 18 ; nombre moyen d'arrivée par heure = 50
    
    try:
        jour_courant = 1
        while jour_courant <= nb_jours:
            print(f"Simulation du {h.date_exacte()}\n")
            
            # Simuler les 24 heures de la journée
            for heure in range(24):
                h.suivant_heure()
                
                # Afficher un rapport toutes les 6 heures
                if heure % 24 == 0:
                    print(h)
                    time.sleep(0.07)  # Pause courte pour l'affichage
            
            # Le jour est automatiquement incrémenté dans suivant_heure
            jour_courant += 1
            
    except KeyboardInterrupt:
        print("\nSimulation interrompue par l'utilisateur.")
    finally:
        h.afficher_bilan_final()


if __name__ == "__main__":
    # Par défaut, on simule sur 365 jours, mais on peut changer cette valeur
    run(365)