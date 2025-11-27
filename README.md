# Medical-AI: Hospital Simulation & AI Prediction System
**Cliquez ici pour la [🇫🇷 version française](README.fr.md):**
> ARTISHOW - Telecom Paris
> Carl MONNAERT, Maxence GUINZIEMBA-PROKOP, Arsène MALLET, Lukas TABOURI

---

> [!CAUTION]
> The project is still under development.
> To follow the indicative progress of our project, see the [planning](./PLANNING.md)

A comprehensive hospital simulation system integrating discrete event simulation, real-time monitoring, machine learning predictions and interactive dashboards.

## Features

### Main simulation

- **Discrete event simulation**: Realistic modelling of hospital operations (arrivals, treatments, planning)
- **Multi-specialities**: Different medical specialities with varying treatment characteristics
- **Dynamic resource management**: Intelligent allocation of doctors and optimisation of patient flows
- **Realistic patient patterns**: Time-dependent arrivals and special events

### Interactive dashboards

- **Real-time monitoring**: Live hospital statistics with automatic refresh
- **Analytical table**: Analysis of patient flows, waiting times, resource utilisation
- **Incident detection**: Automatic identification of operational problems
- **Responsive design**: Compatible with PCs, tablets and mobile devices

### AI predictions
- **Hazard prediction**: ML models to predict overload, long waits, understaffing
- **Multi-horizon forecasting**: From 1 hour to 1 week in advance
- **Risk assessment**: Real-time hazard score with visual indicators
- **Predictive analytics**: Prediction of future volumes and waiting times

### Data analysis

- **Interactive visualisations**: Dynamic graphs (Chart.js)
- **Performance metrics**: Doctor efficiency, patient satisfaction, system usage
- **Trend analysis**: History and seasonal variations
- **Multiple trajectories**: Generation of alternative scenarios based on history

### Trajectory generation

The system can generate multiple trajectories to explore different future scenarios:

```bash
# Generate 50 30-day trajectories for simulation 1
python -m src.simulation.sim_utils trajectories 1 --num=50 --days=30

# Analyse the results
python -m src.simulation.sim_utils analyse 1

# View the results in the dashboard
# Go to http://localhost:8080/trajectories/1
```

**Requirements**: The base simulation must have at least 1 month of data.

## System architecture

```plain
ia-medical/
├── main.py                    # Main entry point
├── src/
│   ├── simulation/           # Simulation engine
│   ├── ml/                  # Machine learning models
│   ├── data/                # Database handling
│   ├── visualizations/     # Web dashboard and UI
│   │   ├── dashboard.py         # Flask software and API routes
│   │   ├── predictions.py       # Flask endpoint pour for AI forecasting
│   │   ├── templates/
│   │   │   ├── index.html
│   │   │   ├── analytics.html
│   │   │   ├── incidents.html
│   │   │   ├── realtime.html
│   │   │   ├── predictions.html
│   │   │   └── trajectories.html
│   │   └── static/
│   │       ├── css/
│   │       │   └── dashboard.css
│   │       └── js/
│   │           ├── dashboard.js
│   │           ├── analytics.js
│   │           ├── incidents.js
│   │           ├── realtime.js
│   │           ├── predictions.js
│   │           └── trajectories.js
│   ├── run_simulation.py   # Simulation starting
│   ├── run_dashboard.py    # Dashboard starting
│   ├── run_ml.py           # Machine learning operations
│   └── config.py           # Parameters
├── requirements.txt
└── README.md
```
## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ia-medical

# Install dependencies
pip install -r requirements.txt
```

### Basic usage

```bash
# Run simulation + dashboard (recommended)
python main.py --simulation --dashboard --doctors=25 --rate=15

# Or run the components separately:
python main.py --simulation --doctors=20 --duration=5
python main.py --dashboard --port=8080
python main.py --ml --train
python main.py --ml --predict --sim-id=1

# Generate documentation
python main.py --docs
```

### Accessing the dashboard

Once launched, access the web interface:

- **Main dashboard**: `http://localhost:8080`
- **Analytics**: `http://localhost:8080/analytics/{sim_id}`
- **AI predictions**: `http://localhost:8080/predictions/{sim_id}`
- **Real time**: `http://localhost:8080/realtime/{sim_id}`
- **Incidents**: `http://localhost:8080/incidents/{sim_id}`
- **Trajectories**: `http://localhost:8080/trajectories/{sim_id}`

## AI prediction system

### Types of hazards detected

1. **Surcharge patient**: Too many patients relative to capacity
2. **Longues attentes**: Average wait time > 60 minutes
3. **Sous-effectif**: Doctor utilisation > 90%
4. **Stress système**: Overall stress indicator

### Time horizons
- **Immédiat** (1 hour): Real-time risk
- **Court terme** (6 hours): Operational planning
- **Moyen terme** (1 day): Resource planning
- **Long terme** (1 week): Strategy

### Training ML models

```bash
# Train all models on historical data
python main.py --ml --train

# Direct training
python src/run_ml.py --train

# List simulations
python src/run_ml.py --list
```

### Obtaining predictions

```bash
# Predictions for a simulation
python main.py --ml --predict --sim-id=1

# Direct prediction
python src/run_ml.py --predict 1
```

## Dashboard pages

### Main dashboard (/)

- List of available simulations
- Simulation statistics and status
- Quick navigation
- Simulation selection

### Analytics (/analytics/{sim_id})

- **Flux patients**: Track the number of patients over time
- **Utilisation médecins**: Efficiency and periods of high activity
- **Modèles horaires**: Identification of peaks
- **Répartition maladies**: Pie charts
- **Métriques quotidiennes**: Performance by day
- **performance médecins**: Individual statistics

### Incidents (/incidents/{sim_id})

- **Alertes forte attente**: Periods of excessive waiting times
- **Incidents occupation**: Too many doctors busy
- **Chronologie évènements**: Epidemics, disasters, etc.
- **Pires cas patients**: Longest waiting times
- **Analyse motifs**: Frequency by hour/type

### Real time (/realtime/{sim_id})
- **Contrôles lecture**: Play/pause/stop, speed
- **Métriques en direct**: Current patients and doctors
- **Graphiques activité**: 2-hour sliding window
- **Evènements récents**: Live feed
- **Statut médecins**: Real-time assignments
- **Alertes**: Active warnings

### Predictions (/predictions/{sim_id})

- **Prédictions de dangers**: Overload, waiting, understaffing, etc.
- **Scores de danger**: Current and future scores (short, medium, long term)
- **Explications modèles**: Influential variables, critical thresholds
- **Historique alertes prédictives**: Periods anticipated by AI
- **Comparaison réel vs prédit**: Comparative graphs between predicted and realized

### Trajectories (/trajectories/{sim_id})

- **Analyse multi-scénarios**: 50+ alternative trajectories for the future
- **Intervalles de confiance**: 25th, 50th, and 75th percentiles of results
- **Statistiques comparatives**: Mean, median, standard deviation per metric
- **Scénarios extrêmes**: Identification of best and worst cases
- **Distribution des résultats**: Histograms of final values
- **Analyse détaillée**: Individual exploration of trajectories

## Configuration

### Simulation parameters

```bash
# Basic simulation
python main.py --simulation --doctors=20 --rate=15 --duration=5

# Advanced configuration
python main.py --simulation \
  --doctors=30 \
  --rate=25 \
  --duration=10
```

### Dashboard options
```bash
# Custom port and host
python main.py --dashboard --port=8080 --host=0.0.0.0

# Debug mode
python main.py --dashboard --debug
```

### Key parameters (src/config.py)

- `SPECIALTIES`: Medical specialities and characteristics
- `PATIENT_ARRIVAL_RATE`: Basic patient arrivals
- `TREATMENT_TIME_RANGES`: Min/max treatment times
- `DISEASE_PROBABILITIES`: Probabilities of pathologies
- `DANGER_THRESHOLDS`: ML risk thresholds

## Database schema

### Main tables

- **`hospital_state`**: Timestamped hospital states
- **`patient_treated`**: Complete treatment history
- **`doctor_activity`**: Doctor activity logs
- **`incidents`**: Detected incidents and alerts
- **`ml_predictions`**: AI predictions and confidence scores

A complete diagram of the database:

![database_diagram](./img/database_diagram.svg)

### Example queries

```sql
-- Simulation summary
SELECT simulation_id, COUNT(*) as patients,
       AVG(wait_time) as avg_wait
FROM patient_treated
GROUP BY simulation_id;

-- Risk periods
SELECT datetime, patients_waiting, doctors_busy
FROM hospital_state
WHERE patients_waiting > 20;
```

## REST API

### Endpoints

```bash
# Simulation data
GET /api/simulation/{id}/data

# Predictions
GET /api/simulation/{id}/predictions

# Train models
POST /api/ml/train

# Real-time updates
GET /api/simulation/{id}/realtime

# Incidents
GET /api/simulation/{id}/incidents
```

### CLI commands
```bash
# Simulation operations
python main.py --simulation [options]
python main.py --dashboard [options]
python main.py --ml [options]

# Direct access to components
python src/run_simulation.py [options]
python src/run_dashboard.py [options]
python src/run_ml.py [options]
```

## Dependencies

### Main dependencies

- **Python 3.8+**
- **Flask 2.3+** - Web framework
- **NumPy 1.24+** - Numerical computation
- **Pandas 1.5+** - Data manipulation
- **SimPy 4.0+** - Discrete event simulation

### ML dependencies

- **scikit-learn 1.3+** - Machine learning
- **joblib 1.1+** - Model saving
- **matplotlib 3.7+** - Graphics
- **seaborn 0.12+** - Statistical visualisation

### Frontend

- **Chart.js 4.0+** - Interactive graphics (CDN)
- **Bootstrap 5.1+** - UI (CDN)
- **Font Awesome 6.0+** - Icons (CDN)

## Presentation poster
![poster](./img/poster-ia-medical.svg)

## Licence

The project is licensed under MIT, more information [here](./LICENSE).
