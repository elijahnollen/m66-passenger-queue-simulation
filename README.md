# M66 Passenger Queue Simulation

This repository contains the code, data, outputs, and documentation for the project **Passenger Queue Dynamics and Waiting-Time Simulation for Selected M66 Bus Stops**.

The project uses 2025 MTA Bus Stop Level Ridership data together with an MTA Manhattan GTFS schedule to model passenger queues and bus loading at five selected eastbound M66 stops. A discrete-event simulation is used to evaluate passenger waiting time, queue buildup, final backlog, and bus occupancy.

The project also uses simulation-based service optimization. Genetic Algorithm (GA), Simulated Annealing (SA), and Particle Swarm Optimization (PSO) were compared as candidate optimization techniques during the Midterm phase. GA was selected as the optimization technique for the succeeding project phase.

## Current Project Status

### Completed

- Data filtering, cleaning, and data-quality checks
- GTFS service and stop mapping
- Dataset analysis and visualizations
- Baseline discrete-event simulation
- 30-replication baseline experiment
- Baseline precision checks
- GA, SA, and PSO optimization screening
- Selection of GA as the final optimization technique
- Preliminary comparison between the published GTFS reference service and the selected optimized service plan

### Planned for the Pre-Final Phase

- High-demand scenario with a 40% increase in passenger demand
- Reduced-service scenario with one scheduled trip removed per study hour
- Combined high-demand and reduced-service scenario
- GA optimization under all operating conditions
- Final scenario comparisons
- Additional validation and sensitivity analysis
- Additional simulation tables and visualizations

The committed processed data, tables, figures, and notebook outputs currently represent the completed Midterm-stage work.

## Repository Structure

```text
m66-passenger-queue-simulation/
├── MODESIM_Project/
│   ├── code/
│   │   ├── m66_dataset_analysis.ipynb
│   │   ├── m66_baseline_simulation.ipynb
│   │   └── README.md
│   │
│   ├── data/
│   │   ├── raw/
│   │   │   ├── MTA_M66_Eastbound_2025_RAW.csv
│   │   │   └── gtfs_m/
│   │   └── processed/
│   │
│   ├── docs/
│   │   ├── MODESIM_Paper/
│   │   ├── Screenshots/
│   │   ├── MTA_BusStopLevelRidership_DataDictionary.pdf
│   │   └── MTA_BusStopLevelRidership_Overview.pdf
│   │
│   └── output/
│       ├── figures/
│       └── tables/
│
├── .gitignore
├── requirements.txt
└── README.md
```

## Main Notebooks

### `m66_dataset_analysis.ipynb`

Performs the dataset preparation and analysis used by the project, including:

- M66 ridership filtering
- Data cleaning and quality checks
- Stop ID history analysis
- GTFS stop and service mapping
- Descriptive statistics
- Demand and service summaries
- Dataset-analysis tables and figures
- Creation of the cleaned dataset used by the simulation

### `m66_baseline_simulation.ipynb`

Contains the current simulation and optimization work, including:

- Representative passenger-demand preparation
- GTFS service-plan construction
- Passenger-stream generation
- Discrete-event passenger queue simulation
- 30-replication baseline experiment
- Precision checking
- GA, SA, and PSO optimization screening
- Optimization-technique selection
- Preliminary comparison between the GTFS reference service and the selected optimized service plan

## Data and Output Folders

### `MODESIM_Project/data/raw/`

Contains the project input files, including the M66 ridership extract and GTFS source files.

### `MODESIM_Project/data/processed/`

Contains cleaned data and reusable simulation files, including:

- Cleaned selected-stop ridership data
- Replication seeds
- Master passenger streams
- Replication-level baseline results
- Precision-check results

### `MODESIM_Project/output/tables/`

Contains summary tables generated for dataset analysis, simulation evaluation, optimization evaluation, and reporting.

### `MODESIM_Project/output/figures/`

Contains generated charts and visualizations used for project analysis and documentation.

## Environment

The project was developed using **Python 3.13.5**.

Main Python libraries:

- NumPy
- pandas
- Matplotlib
- SciPy
- JupyterLab

The required libraries are listed in:

```text
requirements.txt
```

## Setup

Clone the repository:

```bash
git clone https://github.com/elijahnollen/m66-passenger-queue-simulation.git
```

Enter the repository:

```bash
cd m66-passenger-queue-simulation
```

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

## Running the Notebooks

The notebooks should be executed in this order:

1. `m66_dataset_analysis.ipynb`
2. `m66_baseline_simulation.ipynb`

The dataset-analysis notebook prepares the cleaned dataset and supporting files used by the simulation notebook.

The notebooks currently use paths relative to:

```text
MODESIM_Project/code/
```

Use that folder as the working directory.

From the repository root:

```bash
cd MODESIM_Project/code
jupyter lab
```

Then open and execute the notebooks in the order listed above.

Generated files are stored under:

```text
../data/processed/
../output/tables/
../output/figures/
```

## Reproducibility

The project includes the data, simulation inputs, random seeds, outputs, and documentation needed to support repeatable analysis.

Stored replication seeds are used to reproduce the stochastic passenger-arrival process.

Reusable master passenger streams support matched comparisons between corresponding simulation alternatives. This reduces unnecessary variation caused only by different random passenger arrivals.

Reference and optimized service plans use matched simulation replications whenever applicable.

The repository preserves:

- Original project input data
- Cleaned project data
- GTFS source files
- Replication seeds
- Master passenger streams
- Replication-level simulation results
- Summary tables
- Generated figures
- Notebook source code
- Project reports and supporting documentation

Generated CSV and PNG files use fixed filenames. Rerunning the notebooks can replace existing files with the same names.

## Simulation Scope

The simulation represents five consecutive eastbound M66 stops in Manhattan during two study periods:

- **Morning:** 6:00 AM to 11:00 AM
- **Evening:** 3:00 PM to 8:00 PM

The simulation uses published GTFS bus times as the reference service schedule.

Representative passenger demand is derived from cleaned historical MTA Bus Stop Level Ridership data. Passenger arrival times are generated within each study hour.

Passengers wait using a first-in, first-out queue.

A modeled bus capacity of **60 passengers** is used as a project assumption.

Passenger generation stops at the study-period boundary. Eligible buses are allowed to complete their remaining modeled stop events. Passengers still waiting after the final eligible bus are recorded as the **final backlog**.

The model does not attempt to reconstruct actual historical traffic conditions, bus bunching, cancellations, or observed dwell-time variation.

## Experimental Design

The project defines one baseline condition and three stress-test conditions.

### Baseline

Representative passenger demand with the published GTFS reference service.

### High-Demand Scenario

Passenger demand is increased uniformly by 40% while the reference service remains unchanged.

### Reduced-Service Scenario

Representative passenger demand is retained while one scheduled trip is removed from every study hour.

### Combined Scenario

Passenger demand is increased by 40% while one scheduled trip is also removed from every study hour.

The three stress-test scenarios are planned for the Pre-Final implementation phase.

## AI Optimization

The AI role of the project is **simulation-based service optimization**.

Three candidate optimization techniques were evaluated during the Midterm phase:

- Genetic Algorithm
- Simulated Annealing
- Particle Swarm Optimization

Each technique generated candidate hourly service allocations that were evaluated using the passenger-queue simulation.

GA was selected as the final optimization technique based on the completed Midterm screening experiment.

The optimizer changes the hourly distribution of the available service while keeping the total service budget fixed for the corresponding operating condition.

Candidate optimized service plans are evaluated through simulation before they are accepted.

A final-backlog feasibility safeguard is used so that a service plan cannot be considered better only because it lowers completed passenger waiting time while leaving more passengers unserved.

## Main Evaluation Metrics

The simulation uses the following performance measures:

- Mean completed passenger waiting time
- 95th percentile completed passenger waiting time
- Peak queue
- Period-end queue
- Final backlog
- Mean bus occupancy
- Maximum bus occupancy
- Passenger conservation

Paired comparisons and 95% confidence intervals are used when comparing corresponding reference and optimized simulation results.

## Data Sources

The project uses:

- **MTA Bus Stop Level Ridership: Beginning 2024**, filtered to 2025 eastbound M66 records
- **MTA static Manhattan GTFS data**, used as the scheduled bus-service reference

The ridership dataset provides historical passenger activity, while the GTFS feed provides the scheduled service used by the simulation.

The ridership records and GTFS schedule represent different time periods. Because of this, the project is treated as a **controlled simulation and sensitivity study**, not as a reconstruction of one historical M66 operating day.

## Documentation

Supporting project documentation is stored in:

```text
MODESIM_Project/docs/
```

This includes:

- Initial project system representation
- Midterm project report
- MTA dataset documentation
- Data-source and filtering screenshots
- Supporting project materials