# M66 passenger queue simulation and service optimization

This project uses discrete-event simulation to study passenger queues at five eastbound M66 bus stops in Manhattan. It combines 2025 MTA stop-level ridership records with a frozen Manhattan GTFS schedule and uses a genetic algorithm (GA) to compare hourly bus allocations.

The aim is to find service plans that reduce waiting time while keeping the same trip budget and checking how many passengers remain waiting. The model supports planning comparisons under its stated assumptions. Its results need field testing before they can guide actual bus operations.

## Project scope

- Five eastbound stops, covering Stop Sequences 6 through 10.
- Weekday morning period: 06:00 to 11:00.
- Weekday evening period: 15:00 to 20:00.
- Four conditions: baseline, 40 percent higher selected-stop demand, one trip removed per study hour, and both stresses combined.
- Measures: mean and P95 completed waiting time, peak queue, period-end queue, final backlog, and bus occupancy.

The GA chooses five whole hourly trip counts. Each plan keeps its scenario's trip budget and hourly bounds. Candidate buses use even spacing within each hour. A shared simulation engine keeps passenger handling, capacity, and bus-load rules consistent across experiments.

## Repository folders

| Path | Contents |
| --- | --- |
| `MODESIM_Project/code/` | Four notebooks, shared Python modules, and run tools |
| `MODESIM_Project/data/raw/` | Frozen ridership and GTFS inputs |
| `MODESIM_Project/data/processed/` | Cleaned demand, passenger streams, and processed results |
| `MODESIM_Project/output/tables/` | Experiment results, model checks, and comparisons |
| `MODESIM_Project/output/figures/` | Saved plots |
| `MODESIM_Project/docs/` | Technical documentation, reports, and notebook PDFs |

## Setup

Use Python 3.12. From the repository root, create a virtual environment:

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the model dependencies and notebook tools:

```bash
python -m pip install -r requirements-notebooks.txt
python -m jupyterlab MODESIM_Project/code
```

`requirements-notebooks.txt` also installs the pinned model dependencies from `requirements.txt`.

## Run the notebooks

Run each notebook from the first cell in this order. Use a fresh kernel for each notebook, wait for all cells to finish, then save it with its outputs.

| Order | Notebook | Purpose |
| --- | --- | --- |
| 1 | `m66_dataset_analysis.ipynb` | Clean the ridership data, check GTFS mappings, and describe demand |
| 2 | `m66_baseline_simulation.ipynb` | Run baseline replications and the GA, SA, and PSO technique screen |
| 3 | `m66_scenario_simulation.ipynb` | Compare baseline, high demand, reduced service, and combined conditions |
| 4 | `m66_ga_optimization.ipynb` | Search for service plans and test frozen plans on unused passenger seeds |

Run the notebooks with `MODESIM_Project/code/` as their working folder. They import `m66_core.py`, `m66_support.py`, and `m66_evaluation.py` from that folder.

For an optional script run, install `requirements.txt` and run this command from the repository root:

```bash
python MODESIM_Project/code/run_all.py
```

The runner executes the notebooks in order, stops on an error, and generates the comparison figures. It saves plain-text notebook outputs and separate figure files. Use JupyterLab when preparing notebooks with tables and plots displayed inside them.

To generate the extra independent-test figures after a Jupyter run:

```bash
python MODESIM_Project/code/plot_results.py
```

A run writes to the existing result filenames. Keep a copy of any results you need to preserve before rerunning.

## Read the results

The GA search evaluates 100 unique plans per optimizer seed, using three optimizer seeds and five matched passenger replications for fitness. Candidate selection uses a larger matched selection set and checks that mean final backlog does not exceed the reference. The final plans are frozen before a separate test on 30 unused passenger seeds.

The independent test compares GA with the published GTFS reference, a regularized reference, and a simple demand rule. The regularized reference keeps the hourly GTFS trip counts but uses the same spacing rules as GA. This helps distinguish the effect of bus spacing from the effect of allocating trips to different hours.

| Table | What it contains |
| --- | --- |
| `ga_search_history.csv` | Search progress for each scenario, period, and optimizer seed |
| `ga_scenario_selected_plan_replications.csv` | Selected-plan replication results |
| `review_frozen_plans.csv` | Plans fixed before the independent test |
| `review_holdout_paired_comparisons.csv` | Paired differences and confidence intervals on unused seeds |
| `review_holdout_stop_comparisons.csv` | Stop-level waiting and queue tradeoffs |
| `review_holdout_stress_vs_baseline.csv` | Stress conditions compared with baseline |

These tables are in `MODESIM_Project/output/tables/`. Files with the `review_` prefix contain the independent-test experiment. Files with the `exploratory_90901_` prefix record an earlier exploratory experiment, which informed the search design and is separate from the final test.

Read completed waiting time together with backlog. Completed-wait metrics exclude passengers who never board. GA can improve the period mean while increasing wait at individual stops, and it can lose to the demand rule in some comparisons. The limited search does not establish a global optimum.

## Model assumptions

Historical boardings act as a demand proxy. Each stop-hour has a fixed rounded passenger count, with arrival times sampled uniformly within the hour. The model assumes a 60-passenger capacity and deterministic travel offsets. It does not model traffic delays, dwell times, bus bunching, or fleet circulation.

The 2025 ridership records and the June 27 to September 5, 2026 GTFS feed represent a controlled demand-and-schedule comparison. They do not reconstruct a specific operating day. Queues start empty in each period. The simulation processes the eligible bus events and reports any remaining backlog; it does not add buses to clear it.

See [Technical documentation](MODESIM_Project/docs/TECHNICAL_DOCUMENTATION.md) for event rules, input checks, service budgets, statistical comparisons, and experiment design.

## Data sources

- [MTA Bus Stop Level Ridership: Beginning 2024](https://data.ny.gov/Transportation/MTA-Bus-Stop-Level-Ridership-Beginning-2024/fvdm-uavx): historical stop-level boarding and alighting records.
- [MTA developer resources](https://www.mta.info/developers): static GTFS transit schedules.

The frozen inputs in `data/raw/` are used for the experiments. Source links and their uses are documented alongside the relevant notebook code.
