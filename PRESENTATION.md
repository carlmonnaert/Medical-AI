# Présentation du projet

## Introduction - 1min

**Contenu du projet :**  Bonjour, notre projet développe un tableau de bord interactif pour suivre en temps réel l'activité hospitalière : arrivées de patients, pathologies et disponibilité des médecins. Nous avons utilisé l'IA pour déterminer les périodes où l'hôpital risque d'être saturé. 

---

**Objectifs du projet :**  L'objectif final de notre projet est de créer un outil qui aide les gestionnaires d'hopitaux à mieux organiser les ressources, anticiper les moments de forte affluence et optimiser la prise en charge des patients en s'appuyant sur les données réelles de leurs hôpital.

## Mathématique du modéle - 1min - Carl 






## Simalution numérique - 2min - Maxence 

Étant donné que nous avons rencontré beaucoup de difficultés pour trouver des données propres et utilisable pour notre projet. Notre encadrant nous a invité a créer notre propre simulation de donnée pour avoir une base sur laquelle s’appuyer. L’objectif était simple, nous devions simuler 

- les différentes maladies fréquentes présentes dans les hôpitaux avec leurs saisonnalité et leurs durées moyennes de traitement
- l’arrivée aléatoire des patients
- les différentes spécialités des médecins 
- la gestion des flux avec de le modéle de file d’attente que Carl vous a présenté

Pour ce faire, nous avons 3 trois classes sur Python : **Hopital, Médecin et Personne **

Concernant la classe **Médécin**, on y trouve que chaque médecin possède sa spécialité, sa propre file d'attente et son statut d'occupation, permettant une gestion réaliste des ressources.

Dans la classe **Personne**, on crée des arrivées de patients suivent une loi de Poisson avec paramètre λ configurable (patients/heure). Chaque patient se voit attribuer une pathologie selon une distribution pondérée qui varie selon la saisonnalité (26 maladies modélisées avec facteurs mensuels).

Dans la classe **Hopital**, on gére la simulation qui avance par pas de 1 minute, avec suivi horaire, journalier et mensuel. Les temps de traitement suivent des lois exponentielles basées sur les durées moyennes par pathologie.

Au sorti de la simulation, le système génère automatiquement 5 fichiers CSV : **données horaires détaillées, statistiques journalières par pathologie, traitements effectués, bilans mensuels et métriques globales de performance hospitalière** qui seront transféré à Arsene et Lukas pour le dashboard. 



## Gestion des datas - 2min - Arsène

Notre projet utilise *SQLite* comme base de données principale, optimisée pour les performances avec des techniques avancées :
    - Mode WAL pour l'accès concurrent
    - Système de cache et d'optimisations I/O
    - Structure modulaire avec 8 tables spécialisées

- Collecte de Données Multi-Dimensionnelle
- Nous capturons 3 niveaux de granularité/détail:
    - États hospitaliers (patients, médecins, temps d'attente) - temps réel
    - Traitements patients (spécialité, maladie, temps) - granulaire
    - Événements détaillés (arrivées, assignations) - trace complète

Ensuite pour que ces données soient accessibles depuis l'interface, mise en place d'une API RESTful avec Flask, qui permet ensuite à Lukas, qui gère l'app web en tant que telle, de posséder les données avec un format "standardiser", pour ensuite implémentater la logique de visualisation.

## Machine Learning - 1min - Carl 




