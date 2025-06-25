# Présentation du projet

## Introduction - 1min

    - **(Contenu du projet)** : 
    - **(Objectifs du projet)** : 

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






