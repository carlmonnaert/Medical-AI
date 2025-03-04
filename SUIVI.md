# SUIVI - ARTISHOW - IA MEDICAL
> Maxence GUINZIEMBA-PROKOP, Arsene MALLET, Carl MONNAERT, Lukas TABOURI

## 14/02


- Découverte du sujet et mise en place d'un plan d'action pour la réalisation du projet. Nous nous sommes mis d'accord sur language que nous allions utilisé pour la simulation (Python) et les bibliothèques utiles.

- **(Tout le monde)** Carl et Lukas commencé la première simulation assez rapide du problème tant dis que Maxence et Arsène ont commencé à faire des recherches bibliographiques pour comprendre comment avoir une simulation et un modéle mathématique qui s'approche de la réalité (structure.py).


## 18/02

- **(Carl)** La première modélisation a bien fonctionné, nous avons modélisé une seule maladie avec un certain taux de contagion, de mortalité et de "récupération". Cependant, elle rencontre deux problémes majeures qu'il faudra corriger : une complexité qui devient trop importante au fil des jours et une mauvaise gestion des modéles mathématiques (ce qui est normal à ce stade).
- **(Maxence, Lukas)** C'est notre rôle de trouver et comprendre les mathématiques derriere la gestion des patients au sein d'un hopital. Nous avons découvert une revue scientifique ("Modélisation d'un file d'attente" : https://math.univ-lyon1.fr/~alachal/serveurOT/files_attente.pdf) et allons nous inspirer du modele utilisé dans les centres d'appel ie la loi d'Erlang, nous sommes dans la phase de compréhension de ce modéle et de détermination des hypothèses que nous allons faire.
-  De son côté, **(Arsène)** a trouvé des bases de données open source très intéressantes dans lequel on peut trouver le temps moyen que chaque patient attend dans l'hopital, le nombre de lit, le nombre de patient qui reste plus de 3 mois. Et toutes ces informations sur les 15 dernières années.

## 20/02
- **(Tous)** : RDV avec M. Clemençon (encadrant du projet), pour se mettre au point sur le projet, et lui poser nos questions :
    - Q : *Quelle est le livrable attendu du projet ?*
        - R : MINIMUM -> simulation d'hôpital simple + dashboard visualisation | OBJECTIF -> Avancer le + possible simulation/dashboard dans le but d'avoir un prototype intéressant pour un service de santé.
    - Q : *Comment peut-on accéder à des données réelles pour comparer nos simulations/entrainer de futurs modèles de prédiction ?* 
        - R: Impossible d'en avoir, sujet trop sensible, se contenter de faire des hypothèses les + "réalistes" possibles.
    - Mise en garde : Communication cruciale, Commencer par des choses simples puis incrémenter, Discuter de l'avancement fréquemment.
    - Proposition de ressources : *Processus ponctuel marqué*, Méthode de dvpt *agile*.

## 21/02

 - **(Tous)** : mise en place du planning -> Affectation des "rôles"/tâches de chacun et de leur répartition dans l'avancement du projet.

## 04/03
- **(Carl)** Nous avons réalisé des dernières modifications sur la simulation pour optimiser notre algorithme de simulation. Pour des questions de temps de calcul on se restreindra d'abbord à un seul hopital puis lorsque suffisament de fonctionalitées seront disponibles nous ajouterons une dimension spatiale etc. Pour la suite, je suis en train de suivre le cours de typescript en accéléré et de me renseigner sur la manière d'afficher nos graphes en temps réel, soit en faisant tourner le code côté client, soit en intérogeant seulement une base de donnée que nous aurons rempli préalablement avec nos résultats de simulations.