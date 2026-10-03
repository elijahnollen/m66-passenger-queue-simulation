# M66 Passenger Queue Simulation

This repository contains the code, data, outputs, and documentation for the project **Passenger Queue Dynamics and Waiting-Time Simulation for Selected M66 Bus Stops**.

The project uses 2025 MTA Bus Stop Level Ridership data together with a frozen MTA Manhattan GTFS schedule to model passenger queues and bus loading at five selected eastbound M66 stops. A discrete-event simulation evaluates waiting time, queue buildup, final backlog, and bus occupancy. A Genetic Algorithm (GA) is used for simulation-based service optimization.

## Current Project Status

The current repository includes the substantially complete Pre-Final implementation:

- reproducible dataset filtering, cleaning, and data-quality checks
- verified GTFS stop and service mapping
- Baseline discrete-event simulation
- 30-replication Baseline experiment and precision checks
- GA, Simulated Annealing (SA), and Particle Swarm Optimization (PSO) screening
- selection of GA as the final optimization technique
- High-Demand, Reduced-Service, and Combined scenarios
- GA optimization for Baseline, High-Demand, Reduced-Service, and Combined conditions
- final-backlog safeguards
- replication-level validation
- precision checks
- paired reference-versus-GA comparisons with 95% confidence intervals
- stop-level results
- exported reviewer-facing tables and figures

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
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   ├── docs/
│   │   ├── TECHNICAL_DOCUMENTATION.md
│   │   ├── MODESIM_Paper/
│   │   └── Screenshots/
│   └── output/
│       ├── figures/
│       └── tables/
├── .github/
├── .gitignore
├── requirements.txt
└── README.md
```

## Documentation Map

Use these files for different purposes:

- **`README.md`**: reviewer entry point, setup, run order, and quick verification
- **`MODESIM_Project/code/README.md`**: notebook-specific run order and dependency summary
- **`MODESIM_Project/docs/TECHNICAL_DOCUMENTATION.md`**: central technical reference for data contracts, simulation rules, scenarios, GA formulation, validation, reproducibility, output ownership, limitations, and technical sources
- **`MODESIM_Project/docs/MODESIM_Paper/`**: formal project reports

## Main Notebooks

### `m66_dataset_analysis.ipynb`

Prepares and analyzes the project inputs, including data filtering, cleaning, quality checks, Stop ID history, GTFS mappings, descriptive statistics, and creation of the cleaned selected-stop dataset.

### `m66_baseline_simulation.ipynb`

Builds and validates the Baseline model, runs the 30-replication Baseline experiment and precision checks, and performs GA/SA/PSO screening used to select GA.

### `m66_scenario_simulation.ipynb`

Evaluates the common simulation engine under four reference conditions:

- Baseline
- High-Demand
- Reduced-Service
- Combined

It also exports the scenario-specific inputs and reference results required by the GA notebook.

### `m66_ga_optimization.ipynb`

Reproduces the Baseline GA result and applies the selected GA to all four operating conditions. It also produces final-backlog safeguards, selected-plan validations, precision checks, paired 95% confidence intervals, and stop-level GA results.

## Environment

The complete four-notebook workflow was validated with **Python 3.12.5**.

Required top-level packages are listed in:

```text
requirements.txt
```

The current dependency set includes:

- NumPy 2.5.3
- pandas 3.0.6
- Matplotlib 3.11.2
- SciPy 1.18.1
- JupyterLab 4.6.4
- ipykernel 7.4.0

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/elijahnollen/m66-passenger-queue-simulation.git
cd m66-passenger-queue-simulation
```

### 2. Create a Python 3.12 virtual environment

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks environment activation, the environment can still be used directly with its Python executable.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Using `python -m pip` helps ensure packages are installed into the same environment that runs the notebooks.

### 4. Register the project kernel

```powershell
python -m ipykernel install --user --name m66-passenger-queue-simulation --display-name "M66 Passenger Queue Simulation"
```

Select the **M66 Passenger Queue Simulation** kernel when Jupyter opens.

## Required Run Order

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

Dependency flow:

```text
Dataset Analysis
      ↓
Baseline Simulation
      ↓
Scenario Simulation
      ↓
GA Optimization
```

The order matters because later notebooks use processed files generated by earlier notebooks.

## Peer Review Quick Run

For the quickest reviewer execution check after completing the environment setup, open:

```text
MODESIM_Project/code/m66_scenario_simulation.ipynb
```

and run the notebook from top to bottom using the **M66 Passenger Queue Simulation** kernel.

This notebook executes the Baseline, High-Demand, Reduced-Service, and Combined reference conditions using the common simulation engine and regenerates the scenario validation tables and figures. Reviewers can use its final validation messages and exported outputs to confirm that the scenario workflow executes successfully.

The complete project reproduction should still follow the four-notebook run order documented above.

## Key Cross-Notebook Inputs

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

For the full producer/consumer map and output ownership, see `MODESIM_Project/docs/TECHNICAL_DOCUMENTATION.md`.

## Quick Check

Important successful checks include messages equivalent to:

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

The GA notebook is normally the longest-running notebook because it evaluates multiple candidate service plans across matched simulation replications.

## Simulation Scope

The model represents five consecutive eastbound M66 stops during:

- **Morning:** 6:00 AM to 11:00 AM
- **Evening:** 3:00 PM to 8:00 PM

The reference condition uses published GTFS bus times. Passenger demand is derived from cleaned historical MTA Bus Stop Level Ridership data. Individual passenger arrival times are generated within each study hour.

Passengers wait in first-in, first-out order. A modeled bus capacity of **60 passengers** is used.

Passenger generation stops at the study-period boundary. Eligible buses complete their remaining modeled stop events. Passengers still waiting after the final eligible bus are recorded as the **final backlog**.

## Scenarios

| Scenario | Demand | Reference service |
|---|---|---|
| Baseline | Baseline selected-stop demand | Published GTFS service |
| High-Demand | +40% selected-stop boarding demand | Published GTFS service |
| Reduced-Service | Baseline selected-stop demand | One reference trip removed from each study hour |
| Combined | High-Demand passenger streams | Reduced-Service condition |

The 40% increase is limited to boarding demand at the five modeled stops. Upstream occupancy and alighting targets are not multiplied by 1.40.

## GA Service Constraints

The GA redistributes each scenario-specific fixed trip budget across the five study hours.

| Scenario | Morning budget | Evening budget | Hourly bounds |
|---|---:|---:|---:|
| Baseline | 43 | 44 | 5 to 12 |
| High-Demand | 43 | 44 | 5 to 12 |
| Reduced-Service | 38 | 39 | 4 to 12 |
| Combined | 38 | 39 | 4 to 12 |

A final-backlog safeguard prevents selection of a plan that appears to improve completed-passenger waiting time only by leaving more passengers unserved than the matching reference service.

## Main Evaluation Metrics

The simulation reports:

- mean completed passenger waiting time
- 95th percentile completed passenger waiting time
- peak queue
- period-end queue
- final backlog
- mean bus occupancy
- maximum bus occupancy
- passenger conservation

Paired comparisons and 95% confidence intervals are used for corresponding reference-versus-GA results.

## Reproducibility Evidence

The repository preserves the main inputs and generated evidence needed for independent review:

- original project input data
- cleaned project data
- frozen GTFS files
- replication seeds
- Baseline and High-Demand master passenger streams
- replication-level simulation results
- scenario reference results
- optimization results
- validation tables
- precision tables
- paired comparison tables
- stop-level results
- generated figures
- notebook source code
- project documentation

The stochastic passenger-arrival process uses reproducible seed sequences. Matched passenger streams are used where applicable so corresponding alternatives can be compared under compatible stochastic demand realizations.

## Technical Documentation

For the detailed implementation specification, data contracts, model assumptions, scenario construction, GA formulation, validation rules, limitations, and technical references, see:

```text
MODESIM_Project/docs/TECHNICAL_DOCUMENTATION.md
```

## Project Reports

Formal project reports are stored under:

```text
MODESIM_Project/docs/MODESIM_Paper/
```
