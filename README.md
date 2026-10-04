# M66 passenger queue simulation

This project studies passenger waiting at five eastbound M66 bus stops in Manhattan. It uses MTA stop-level ridership data, a frozen GTFS bus schedule, and discrete-event simulation to compare service plans. A genetic algorithm (GA) searches for hourly trip allocations under the same trip budget as each scenario's reference service.

The project helps explore how service allocation affects waiting, queues, and passengers left behind. Its results are planning comparisons under stated assumptions. Measured operating data and route-wide feasibility checks are needed before using a plan in actual service.

## What the project covers

- Five eastbound stops, covering stop sequences 6 through 10.
- Weekday morning and evening periods.
- Baseline, higher demand, reduced service, and combined conditions.
- Waiting time, queue lengths, bus occupancy, and passengers still waiting.
- A matched technique screen and an independent test of selected GA plans against reference service and simple service rules.

For model rules, numerical settings, statistics, and limitations, read the [technical documentation](MODESIM_Project/docs/TECHNICAL_DOCUMENTATION.md).

## Repository tree

```text
m66-passenger-queue-simulation/
├── README.md
├── requirements.txt
├── requirements-notebooks.txt
└── MODESIM_Project/
    ├── code/
    │   ├── README.md
    │   ├── m66_dataset_analysis.ipynb
    │   ├── m66_baseline_simulation.ipynb
    │   ├── m66_scenario_simulation.ipynb
    │   ├── m66_ga_optimization.ipynb
    │   ├── m66_core.py
    │   ├── m66_support.py
    │   ├── m66_evaluation.py
    │   ├── plot_results.py
    │   └── run_all.py
    ├── data/
    │   ├── raw/
    │   │   ├── MTA_M66_Eastbound_2025_RAW.csv
    │   │   └── gtfs_m/                  # frozen GTFS text files
    │   └── processed/                   # cleaned and derived CSV files
    ├── docs/
    │   ├── TECHNICAL_DOCUMENTATION.md
    │   ├── MTA_BusStopLevelRidership_DataDictionary.pdf
    │   ├── MTA_BusStopLevelRidership_Overview.pdf
    │   ├── Screenshots/                 # source reference images
    │   ├── MODESIM_Paper/               # submitted project reports
    │   └── code-pdf/                    # notebook PDF copies
    └── output/
        ├── tables/                      # experiment results and checks
        └── figures/                     # saved PNG plots
```

The tree groups generated CSVs, PNGs, and supporting documents instead of listing every output file.

## File guide

| File or folder | What it is for |
| --- | --- |
| `requirements.txt` | Pinned packages needed to run the model and plotting code |
| `requirements-notebooks.txt` | Jupyter tools plus the model packages from `requirements.txt` |
| `m66_dataset_analysis.ipynb` | Cleans input records, checks stop mappings, and describes demand and service |
| `m66_baseline_simulation.ipynb` | Runs baseline replications and compares GA, simulated annealing, and particle swarm optimization |
| `m66_scenario_simulation.ipynb` | Runs reference service under each demand and service condition |
| `m66_ga_optimization.ipynb` | Searches for hourly allocations, selects plans, and tests frozen plans on unused passenger seeds |
| `m66_core.py` | Generates passengers and runs the shared passenger and bus event engine |
| `m66_support.py` | Handles load allocation, input checks, replication checks, and paired comparisons |
| `m66_evaluation.py` | Builds service controls and evaluates frozen plans on the independent test set |
| `plot_results.py` | Draws independent-test figures from saved result tables |
| `run_all.py` | Executes the four notebooks in order and generates comparison figures |
| `data/raw/` | Frozen ridership and GTFS inputs used by the model |
| `data/processed/` | Cleaned demand, generated passenger streams, and derived input tables |
| `output/tables/` | Replication results, selected plans, comparisons, and checks |
| `output/figures/` | Charts generated from the data and experiment results |
| `docs/TECHNICAL_DOCUMENTATION.md` | Full model assumptions, event rules, optimization settings, and statistical methods |
| MTA PDFs and `docs/Screenshots/` | Reference material for interpreting the source data |
| `docs/MODESIM_Paper/` | Project report documents; read the technical documentation for current model rules |
| `docs/code-pdf/` | Readable PDF copies of the executed notebooks; the `.ipynb` files remain the runnable source |
| `code/README.md` | Quick links for working with the code folder |

## Setup

Use Python 3.12. Run these commands from the repository root:

```bash
python -m venv .venv
```

Activate the environment in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the packages and register the notebook kernel:

```bash
python -m pip install -r requirements-notebooks.txt
python -m ipykernel install --user --name m66-passenger-queue-simulation --display-name "M66 Passenger Queue Simulation"
python -m jupyterlab MODESIM_Project/code
```

Choose **M66 Passenger Queue Simulation** as the kernel. Keep both requirements files in the repository so others can install the packages.

## Run the project

Run each notebook from the first cell in this order:

1. `m66_dataset_analysis.ipynb`
2. `m66_baseline_simulation.ipynb`
3. `m66_scenario_simulation.ipynb`
4. `m66_ga_optimization.ipynb`

Use `MODESIM_Project/code/` as the working folder. Restart the kernel before each notebook, run all cells, wait for completion, and save the notebook with its outputs. Keep the shared `.py` modules beside the notebooks.

To run without Jupyter, install the model packages and use:

```bash
python -m pip install -r requirements.txt
python MODESIM_Project/code/run_all.py
```

This runner saves plain-text notebook outputs and separate PNG figures. Use JupyterLab to save notebooks with displayed tables and plots.

To regenerate the independent-test figures from existing result tables:

```bash
python MODESIM_Project/code/plot_results.py
```

A run overwrites existing result filenames. Keep a copy of results you need before rerunning. If a run fails, fix the error and complete the notebook sequence before using the output folders as one result set.

## Reviewer access and a baseline check

This repository is private. Reviewers need repository access or a complete downloaded project folder before using these instructions. A download must include the frozen data, shared modules, notebooks, requirements files, and saved outputs.

After setup, run `m66_dataset_analysis.ipynb` and then `m66_baseline_simulation.ipynb`, restarting the kernel before each. Check that the baseline passenger totals are 500 for Morning and 276 for Evening and that conservation, waiting-time, and occupancy checks pass. This sequence checks baseline behavior; it does not regenerate the independent-test results. Run all four notebooks for those results.

## Measured execution times

The following values are from one successful sequential `run_all.py` execution. The environment used Python 3.12.14. Package installation and file downloads are excluded. Other machines and interactive Jupyter runs can take different amounts of time.

| Stage | Measured seconds | Approximate minutes |
| --- | ---: | ---: |
| `m66_dataset_analysis.ipynb` | 2.9 | 0.05 |
| `m66_baseline_simulation.ipynb` | 41.1 | 0.69 |
| `m66_scenario_simulation.ipynb` | 8.4 | 0.14 |
| `m66_ga_optimization.ipynb` | 348.2 | 5.80 |
| `plot_results.py` | 1.2 | 0.02 |
| `Full sequential run` | 401.8 | 6.70 |

The values are estimates for planning a run, not guaranteed limits. `output/tables/execution_runtime.csv` records the full measurement, environment, and code fingerprint. `run_all.py` measures each future complete execution and replaces the timing table only after success. Its full-run time includes the notebook stages and figure generation. Running the first two notebooks takes about 0.73 minutes in this measured environment.

## Find the results

All table names below are inside `MODESIM_Project/output/tables/`.

| File or group | What to look for |
| --- | --- |
| Baseline and scenario replication, stop, and precision tables | Reference performance and replication checks |
| `ai_*.csv` tables | Matched technique-screen results |
| `ga_search_history.csv` | GA search progress by scenario, period, and optimizer seed |
| `ga_scenario_selected_plan_replications.csv` | Replication results for selected GA plans |
| `ga_output_manifest.csv`, `scenario_output_manifest.csv` | File indexes for the corresponding experiment outputs |
| `review_frozen_plans.csv`, `review_control_plans.csv` | Plans used in the independent test |
| `review_holdout_seeds.csv` | Independent-test passenger seeds |
| `review_holdout_*replications.csv`, `review_holdout_*stops.csv` | Independent-test replication and stop results |
| `review_holdout_paired_comparisons.csv` | Paired performance differences and confidence intervals |
| `review_holdout_stop_comparisons.csv` | Stop-level waiting and queue tradeoffs |
| `review_holdout_stress_vs_baseline.csv` | Stress conditions compared with baseline |
| `review_reference_queue_*.csv` | Reference queue traces used in the comparison figures |
| `review_last_bus_diagnostics.csv`, `review_last_bus_summary.csv` | Stop-specific final eligible bus times and the two components of final backlog |
| `execution_runtime.csv` | Measured notebook and full-run times, with environment details |

The `review_` prefix names the independent-test experiment. Read waiting time together with backlog and stop-level results. Lower mean waiting time does not mean that every passenger or stop benefits. Use the technical documentation to interpret comparisons and confidence intervals.

## Data sources

- [MTA Bus Stop Level Ridership: Beginning 2024](https://data.ny.gov/Transportation/MTA-Bus-Stop-Level-Ridership-Beginning-2024/fvdm-uavx): stop-level boarding and alighting records.
- [MTA developer resources](https://www.mta.info/developers): static transit schedules.

The experiments use the frozen files in `data/raw/`. The notebooks contain the source links and checks used to prepare those inputs.
