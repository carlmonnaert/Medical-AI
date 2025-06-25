# Présenation du projet

## Introduction - 1min

    - **(Contenu du projet)** : 
    - **(Objectifs du projet)** : 

## Gestion des datas - 2min - Arsène

Notre projet utilise *SQLite* comme base de données principale, optimisée pour les performances avec des techniques avancées :

- Mode WAL pour l'accès concurrent
- Cache 10MB et optimisations I/O
- Structure modulaire avec 8 tables spécialisées
- Collecte de Données Multi-Dimensionnelle
- Nous capturons 3 niveaux de granularité :

- États hospitaliers (patients, médecins, temps d'attente) - temps réel
- Traitements patients (spécialité, maladie, temps) - granulaire
- Événements détaillés (arrivées, assignations) - trace complète






