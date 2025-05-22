# Hospital Simulation with Dashboard

This project simulates a hospital with multiple specialties and patients, and provides a web dashboard for real-time monitoring and data visualization. It also includes machine learning components for predictive analytics.

## Project Structure

```
ia-medical/
├── data/                  # Data directory for database and output
├── docs/                  # Documentation
├── src/                   # Source code
│   ├── data/              # Data access modules
│   ├── ml/                # Machine learning modules
│   ├── simulation/        # Hospital simulation components
│   ├── utils/             # Utility functions
│   ├── visualization/     # Dashboard and visualization components
│   ├── config.py          # Configuration settings
│   ├── run_dashboard.py   # Dashboard runner
│   ├── run_ml.py          # ML runner
│   └── run_simulation.py  # Simulation runner
└── main.py                # Main entry point
```

## Setup

1. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the System

You can run the entire system using the main.py script:

```bash
python main.py --all
```

Or run individual components:

```bash
# Run just the simulation
python main.py --simulation

# Run just the dashboard
python main.py --dashboard

# Run just the ML operations
python main.py --ml --train --predict
```

### Simulation Options

- `--resume`: Resume from previous simulation state
- `--doctors=N`: Set the number of doctors (default: 18)
- `--rate=R`: Set patient arrival rate (default: 50 per hour)
- `--minutes=M`: Set simulation duration (default: 525600 minutes = 1 year)

### ML Options

- `--train`: Train ML models
- `--predict`: Generate predictions
- `--days=D`: Number of days to predict (default: 7)

## Documentation

To generate HTML documentation for the project using Sphinx:

```bash
python src/generate_docs.py
```

This will create comprehensive documentation in the `docs/build/html/` directory. Open `docs/build/html/index.html` in your browser to view the documentation.

Alternatively, you can use the provided shell script:

```bash
./generate_docs.sh
```

## Components

### Simulation

The simulation models a hospital with different medical specialties and patient types. It includes:

- Realistic time-of-day and seasonal patterns for patient arrivals
- Multiple doctor specialties with appropriate allocation
- Detailed data collection and visualization
- Ability to pause and resume simulations

### Dashboard

The dashboard provides visualization and analysis of the simulation data:

- Key statistics (total patients, treated patients, busy doctors, waiting patients)
- Hospital activity timeline
- Disease distribution
- Hourly and seasonal patient patterns
- Average wait times by specialty
- Prediction visualizations

### Machine Learning

The ML component provides predictive analytics:

- Patient arrival rate prediction
- Wait time prediction
- Feature engineering and data preprocessing
