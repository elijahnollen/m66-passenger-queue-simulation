# M66 Passenger Queue Simulation

This repository contains the code, data, outputs, and documentation for the project **Passenger Queue Dynamics and Waiting-Time Simulation for Selected M66 Bus Stops**.

The project uses 2025 MTA Bus Stop Level Ridership data together with an MTA Manhattan GTFS schedule to model passenger queues and bus loading at five selected eastbound M66 stops. A discrete-event simulation evaluates passenger waiting time, queue buildup, final backlog, and bus occupancy. A Genetic Algorithm (GA) is then used for simulation-based service optimization.

## Current Project Status

The current repository includes the completed Pre-Final implementation:

- Data filtering, cleaning, and data-quality checks
- GTFS service and stop mapping
- Baseline discrete-event simulation
- 30-replication baseline experiment
- Baseline precision checks
- GA, Simulated Annealing (SA), and Particle Swarm Optimization (PSO) screening
- Selection of GA as the optimization technique
- High-Demand scenario
- Reduced-Service scenario
- Combined High-Demand and Reduced-Service scenario
- GA optimization for Baseline, High-Demand, Reduced-Service, and Combined conditions
- Final-backlog safeguards
- Replication-level validation
- Precision checks
- Paired reference-versus-GA comparisons with 95% confidence intervals
- Stop-level results
- Exported scenario and GA tables for review

## Repository Structure

```text
m66-passenger-queue-simulation/
├── MODESIM_Project/
│   ├── code/
│   │   ├── m66_dataset_analysis.ipynb
│   │   ├── m66_baseline_simulation.ipynb
│   │   ├── m66_scenario_simulation.ipynb
│   │   ├── m66_ga_optimization.ipynb
│   │   └── README.md
│   │
│   ├── data/
│   │   ├── raw/
│   │   │   ├── MTA_M66_Eastbound_2025_RAW.csv
│   │   │   └── gtfs_m/
│   │   └── processed/
│   │
│   ├── docs/
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

Prepares and analyzes the project dataset, including:

- M66 ridership filtering
- Data cleaning and quality checks
- Stop ID history analysis
- GTFS stop and service mapping
- Descriptive statistics
- Demand and service summaries
- Dataset-analysis tables and figures
- Creation of the cleaned selected-stop dataset

### `m66_baseline_simulation.ipynb`

Builds and evaluates the Baseline model, including:

- Representative passenger-demand preparation
- GTFS reference service
- Passenger-stream generation
- Discrete-event passenger queue simulation
- 30-replication baseline experiment
- Precision checking
- GA, SA, and PSO screening
- Baseline GA selection and evaluation

### `m66_scenario_simulation.ipynb`

Evaluates the Baseline and three stress-test conditions using the same simulation engine:

- Baseline
- High-Demand
- Reduced-Service
- Combined

The notebook also exports the scenario inputs and results required by the GA notebook, including the High-Demand master passenger streams and Reduced-Service service plan.

### `m66_ga_optimization.ipynb`

Runs the generalized GA across all operating conditions:

- Baseline reproduction check
- High-Demand GA
- Reduced-Service GA
- Combined GA
- Fixed service-budget and hourly-bound checks
- Final-backlog safeguards
- Selected-plan validation
- Precision checks
- Paired 95% confidence intervals
- Stop-level results
- Exported reviewer-facing GA tables

## Environment

The current notebooks were tested using **Python 3.12**.

Required Python packages are listed in:

```text
requirements.txt
```

The project uses:

- NumPy
- pandas
- Matplotlib
- SciPy
- JupyterLab
- ipykernel

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/elijahnollen/m66-passenger-queue-simulation.git
cd m66-passenger-queue-simulation
```

### 2. Create a project virtual environment

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, the environment can still be used directly with:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Install the required packages

With the virtual environment activated:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Using `python -m pip` is recommended so the packages are installed into the same Python environment that will run the notebooks.

### 4. Register the project Jupyter kernel

```powershell
python -m ipykernel install --user --name m66-passenger-queue-simulation --display-name "M66 Passenger Queue Simulation"
```

When Jupyter opens, select the **M66 Passenger Queue Simulation** kernel.

## Running the Notebooks

The notebooks use paths relative to:

```text
MODESIM_Project/code/
```

From the repository root:

```powershell
cd MODESIM_Project\code
jupyter lab
```

Run the notebooks in this order:

1. `m66_dataset_analysis.ipynb`
2. `m66_baseline_simulation.ipynb`
3. `m66_scenario_simulation.ipynb`
4. `m66_ga_optimization.ipynb`

This order matters because later notebooks use processed files generated by earlier notebooks.

### Dependency Flow

```text
Dataset Analysis
      ↓
Baseline Simulation
      ↓
Scenario Simulation
      ↓
GA Optimization
```

The Scenario notebook generates files used by the GA notebook, including:

```text
../data/processed/M66_HighDemand_Master_Passenger_Streams.csv
../data/processed/M66_HighDemand_Results.csv
../data/processed/M66_ReducedService_Results.csv
../data/processed/M66_Combined_Results.csv
../data/processed/M66_ReducedService_Service_Plan.csv
```

Generated files are stored under:

```text
../data/processed/
../output/tables/
../output/figures/
```

## Reviewer Quick Check

A reviewer can verify the implementation by running the notebooks in the required order and checking the validation messages.

Important successful checks include:

```text
All required validation checks passed: True
All scenarios use the common replication seed pool: True
Scenario configuration matches executed experiment: True
Stop-level result structure valid: True
All expected CSV outputs exported successfully: True
Generalized GA reproduces the Midterm Baseline result: True
All stress-scenario GA safeguards passed: True
All selected-plan validation checks passed: True
All expected GA outputs exported successfully: True
```

The GA notebook is the longest-running notebook because it evaluates multiple candidate service plans across matched simulation replications.

## Reproducibility

The repository preserves the inputs and evidence needed to support repeatable analysis:

- Original project input data
- Cleaned project data
- Frozen GTFS source files
- Replication seeds
- Baseline master passenger streams
- High-Demand master passenger streams
- Replication-level simulation results
- Scenario reference results
- Optimization results
- Validation tables
- Precision tables
- Paired comparison tables
- Stop-level results
- Generated figures
- Notebook source code
- Project documentation

The stochastic passenger-arrival process uses reproducible seed sequences.

Matched passenger streams are used where applicable so corresponding reference and optimized alternatives can be compared using the same stochastic demand realization.

Generated CSV and PNG files use fixed filenames. Rerunning the notebooks can replace existing generated files with the same names.

## Simulation Scope

The simulation represents five consecutive eastbound M66 stops in Manhattan during two study periods:

- **Morning:** 6:00 AM to 11:00 AM
- **Evening:** 3:00 PM to 8:00 PM

The reference condition uses published GTFS bus times.

Representative passenger demand is derived from cleaned historical MTA Bus Stop Level Ridership data. Individual passenger arrival times are generated within each study hour.

Passengers wait using a first-in, first-out queue.

A modeled bus capacity of **60 passengers** is used.

Passenger generation stops at the study-period boundary. Eligible buses are allowed to complete their remaining modeled stop events. Passengers still waiting after the final eligible bus are recorded as the **final backlog**.

The model does not attempt to reconstruct actual historical traffic conditions, bus bunching, cancellations, early running, or observed dwell-time variation.

## Experimental Design

### Baseline

Representative selected-stop passenger demand with the published GTFS reference service.

### High-Demand

Selected-stop boarding demand is increased by 40% while the Baseline reference service is retained.

### Reduced-Service

Baseline selected-stop passenger demand is retained while one reference trip is removed from every study hour.

The Reduced-Service reference has:

- 38 Morning trips
- 39 Evening trips

For GA optimization, the fixed Reduced-Service period budget is redistributed across the five study hours using an hourly search range of **4 to 12 trips**.

### Combined

The High-Demand passenger streams are evaluated together with the Reduced-Service service condition.

The 40% increase applies to boarding demand at the five modeled stops. Upstream occupancy and alighting demand are not multiplied by 1.40.

The Combined GA uses the same Reduced-Service period budgets and the same **4 to 12 trips per hour** search range.

## AI Optimization

The AI role of the project is **simulation-based service optimization**.

Three candidate optimization techniques were evaluated during the Midterm phase:

- Genetic Algorithm
- Simulated Annealing
- Particle Swarm Optimization

GA was selected as the optimization technique for the succeeding project phase.

For each scenario, the GA redistributes the scenario-specific fixed service budget across the five study hours. Candidate schedules are evaluated through the passenger-queue simulation.

A final-backlog safeguard is used so a plan cannot be selected only because it lowers completed-passenger waiting time while leaving more passengers unserved than the corresponding reference service.

## Main Evaluation Metrics

The simulation reports:

- Mean completed passenger waiting time
- 95th percentile completed passenger waiting time
- Peak queue
- Period-end queue
- Final backlog
- Mean bus occupancy
- Maximum bus occupancy
- Passenger conservation

Paired comparisons and 95% confidence intervals are used for corresponding reference-versus-GA results.

## Data Sources

The project uses:

- **MTA Bus Stop Level Ridership: Beginning 2024**, filtered to 2025 eastbound M66 records
- **MTA static Manhattan GTFS data**, used as the scheduled bus-service reference

The ridership records and GTFS schedule represent different time periods. The project is therefore treated as a controlled simulation and sensitivity study rather than a reconstruction of one historical operating day.

## Documentation

Supporting project documentation is stored under:

```text
MODESIM_Project/docs/
```

This includes the project reports, dataset documentation, screenshots, and supporting materials.
