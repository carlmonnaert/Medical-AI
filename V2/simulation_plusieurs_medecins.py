import numpy as np
from numpy import random as rd
from datetime import datetime, timedelta
import time
import sys, os, csv
import random

# Liste des maladies avec leur temps de traitement et spécialiste requis
Maladies = [
    ["infection_virale", 20, "generaliste"],
    ["fracture_legere", 50, "urgentiste"],
    ["plaie_ouverte", 30, "urgentiste"],
    ["crise_asthme", 45, "pneumologue"],
    ["douleurs_abdominales", 60, "generaliste"],
    ["mal_dos_aigu", 30, "generaliste"],
    ["infection_urinaire", 15, "generaliste"],
    ["malaise", 40, "cardiologue"],
    ["gastro-enterite", 40, "generaliste"],
    ["femme_enceinte", 200, "gynecologue"],
    ["avc", 400, "neurologue"],
    ["infarctus", 300, "cardiologue"],
]

# Poids de probabilité pour chaque maladie (ie leurs fréquences d'apparition)
Poids = [27, 20, 10, 6, 7, 6, 5, 5, 3, 3, 2, 1]


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
            "generaliste": int(
                0.237 * nb_medecin
            ),  # 23,7% des médecins généré doivent être des médecins généralistes
            "urgentiste": int(
                0.226 * nb_medecin
            ),  # 22,6% des médecins généré doivent être des médecins généralistes
            "neurologue": int(0.115 * nb_medecin),  # ...
            "cardiologue": int(0.165 * nb_medecin),
            "gynecologue": int(0.161 * nb_medecin),
            "pneumologue": int(0.084 * nb_medecin),
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
            aléatoire = random.randrange(0, 2)
            if aléatoire == 1:
                self.medecins.append(Medecin(id_counter, "generaliste"))
                self.medecins_par_specialite["generaliste"].append(self.medecins[-1])
                id_counter += 1
            else:
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

    def arrivee_patients(self):
        """
        Génère les arrivées de patients et les attribue aux médecins appropriés selon leur spécialité
        """
        if self.prochaine_arrivee <= 0:
            # Nombre de minutes avant la prochaine arrivée (loi de Poisson)
            self.prochaine_arrivee = np.random.exponential(60 / self.lambda_poisson)

            # Choix pondéré d'une des maladies
            choix = random.choices(Maladies, weights=Poids, k=1)[
                0
            ]  # cf les listes en haut du code
            maladie, temps_moyen, specialite_requise = choix

            # Temps de traitement selon une loi exponentielle avec le temps moyen de la maladie
            temps_de_traitement = max(1, int(np.random.exponential(temps_moyen)))

            # Création du patient
            patient = Personne(
                temps_de_traitement, self.dt, maladie, specialite_requise
            )
            db.insert_patient(patient_id, arrival_time, waiting_time, treatment_start_time, treatment_end_time, status):
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
        for medecin in self.medecins:
            if len(medecin.file_attente) > 0:
                medecin.occupe = True
                medecin.file_attente[0].mise_a_jour()
            else:
                medecin.occupe = False

            # Compter les patients traités
            avant = len(medecin.file_attente)
            if medecin.occupe:
                medecin.file_attente = [
                    personne
                    for personne in medecin.file_attente
                    if personne.temps_de_traitement > 0
                ]
            else:
                medecin.file_attente = [
                    personne
                    for personne in medecin.file_attente
                    if personne.temps_de_traitement > 0
                ]
            apres = len(medecin.file_attente)
            patients_traites = avant - apres
            medecin.patients_traites += patients_traites
            self.soignés += patients_traites

    def sauvegarder_data(self):
        nom_fichier = "./data/data_sim.csv"
        entetes = [
            "minute",
            "patients_arrives",
            "patients_traites",
            "patients_en_attente",
            "medecins_occupes",
        ] + [f"file_attente_{m.specialite}_{m.id}" for m in self.medecins]

        ligne = [
            self.temps_total,
            self.patients_totaux,
            self.soignés,
            sum(len(m.file_attente) for m in self.medecins),
            sum(1 for m in self.medecins if m.occupe),
        ] + [len(m.file_attente) for m in self.medecins]

        # Vérifie si le fichier existe pour écrire les en-têtes
        ecrire_entetes = not os.path.exists(nom_fichier)

        with open(nom_fichier, mode="a", newline="") as fichier_csv:
            writer = csv.writer(fichier_csv)
            if ecrire_entetes:
                writer.writerow(entetes)
            writer.writerow(ligne)


    def suivant(self):
        """
        Passe au tour de boucle suivant
        """
        self.arrivee_patients()
        self.mise_a_jour_patients()
        self.sauvegarder_data()

        self.temps_total += self.dt
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

        print("\nEfficacité du système:")
        if self.temps_total > 0:
            patients_par_heure = (self.soignés * 60) / self.temps_total
            print(f"  Moyenne de patients traités par heure: {patients_par_heure:.2f}")

        taux_traitement = (
            (self.soignés / self.patients_totaux * 100)
            if self.patients_totaux > 0
            else 0
        )
        print(f"  Taux de traitement: {taux_traitement:.2f}%")

        print("=" * 50)

        # Quitter proprement le programme
        sys.exit(0)


def run():
    h = Hopital(
        1, 18, 50
    )  # dt = 1 minute ; nombre de médecins = 10 ; nombre moyen d'arrivée par heure = 40
    compte = 0

    try:
        while True:
            print("\n" + "_" * 50)
            print("\nHeure                      :", timedelta(minutes=h.dt * compte))
            h.suivant()
            print(h)  # Appel à __str__ pour afficher l'état
            compte += 1
            time.sleep(0.1)
    except KeyboardInterrupt:
        h.afficher_bilan_final()


if __name__ == "__main__":
    db.initialize_databse()
    run()
