# M66 Passenger Queue Simulation: Technical Documentation

## 1. Purpose

This document is the central technical reference for the M66 passenger queue simulation repository. It explains the project architecture, data flow, simulation rules, scenario definitions, Genetic Algorithm (GA) formulation, validation logic, reproducibility controls, output ownership, and technical references used by the notebooks.

The notebooks remain the executable implementation. This file centralizes material that would otherwise be duplicated across multiple notebooks.

## 2. Project Architecture

The implementation is divided into four notebooks with separate responsibilities.

| Notebook | Primary responsibility | Main downstream dependency |
|---|---|---|
| `m66_dataset_analysis.ipynb` | Filter, clean, validate, map, and summarize the MTA ridership and GTFS inputs | Produces the cleaned selected-stop dataset and supporting mapping/analysis tables |
| `m66_baseline_simulation.ipynb` | Build and validate the Baseline discrete-event simulation, run the 30-replication Baseline experiment, and perform the GA/SA/PSO technique screening | Produces the Baseline passenger streams, replication seeds, Baseline results, precision evidence, and AI-screening evidence |
| `m66_scenario_simulation.ipynb` | Evaluate Baseline, High-Demand, Reduced-Service, and Combined reference conditions using the same simulation rules | Produces scenario reference results and scenario-specific inputs required by the GA notebook |
| `m66_ga_optimization.ipynb` | Reproduce the Baseline GA result and apply the selected GA consistently to Baseline, High-Demand, Reduced-Service, and Combined conditions | Produces optimized plans, validation evidence, paired comparisons, precision checks, and stop-level GA results |

Required execution order:

```text
Dataset Analysis
      ↓
Baseline Simulation
      ↓
Scenario Simulation
      ↓
GA Optimization
```

Later notebooks intentionally depend on generated files from earlier notebooks. The notebooks should therefore be run in the order above when reproducing the full project from source.

## 3. Repository Paths

The project uses the following main directories:

```text
MODESIM_Project/
├── code/              Executable Jupyter notebooks
├── data/
│   ├── raw/           Frozen project input data
│   └── processed/     Cleaned data and simulation-ready intermediate/result files
├── docs/              Project reports, technical documentation, and supporting evidence
└── output/
    ├── figures/       Generated PNG figures
    └── tables/        Generated CSV summaries, checks, and reviewer-facing evidence
```

Generated files use fixed names so a complete rerun replaces the previous generated version rather than creating uncontrolled duplicates.

## 4. Data Sources and Input Roles

### 4.1 MTA Bus Stop Level Ridership

Primary source:

- MTA Bus Stop Level Ridership: Beginning 2024
- https://data.ny.gov/d/fvdm-uavx

The project uses 2025 M66 eastbound ridership records. The selected-stop simulation dataset is restricted to weekday study periods and stop sequences 6 through 10.

Main uses:

- selected-stop boarding demand
- selected-stop alighting targets
- upstream boarding/alighting information used to estimate initial bus occupancy
- descriptive demand summaries
- data-quality and source-absence checks

The ridership source is based on Automatic Passenger Counter observations. Source-absent combinations are not automatically interpreted as zero demand because absence can reflect unavailable APC observations.

### 4.2 MTA Static Manhattan GTFS

Primary source:

- MTA Developer Resources / Static GTFS
- https://www.mta.info/developers

GTFS format reference:

- https://gtfs.org/documentation/schedule/reference/

The repository preserves a frozen GTFS project snapshot under:

```text
MODESIM_Project/data/raw/gtfs_m/
```

Main uses:

- verified M66 weekday service pattern
- exact published Baseline bus arrival times
- trip identifiers
- stop order and stop mapping
- Morning and Evening service budgets
- hour-specific downstream travel-time offsets used to expand candidate GA schedules from Stop 6 to the remaining modeled stops

GTFS provides scheduled service, not observed real-time vehicle movements.

## 5. Selected System Scope

The simulation represents five consecutive eastbound M66 stops:

1. Stop sequence 6: W 65 ST/CENTRAL PARK WEST
2. Stop sequence 7: E 65 ST/5 AV
3. Stop sequence 8: MADISON AV/E 65 ST
4. Stop sequence 9: MADISON AV/E 67 ST
5. Stop sequence 10: E 68 ST/LEXINGTON AV

Study periods:

- Morning: 6:00 AM to 11:00 AM, represented by hours 6 through 10
- Evening: 3:00 PM to 8:00 PM, represented by hours 15 through 19

Morning and Evening are simulated separately.

## 6. Cross-Source Mapping Rule

Historical ridership Stop IDs are not treated as the sole cross-source key because Stop IDs can differ between the historical ridership data and the current GTFS snapshot.

The project therefore relies on a verified combination of:

- Route ID
- Direction
- Stop Sequence
- verified stop name / physical stop mapping

Stop Sequence is the stable route-position identifier used by the simulation queues and stop-level summaries.

## 7. Data Preparation Rules

The Dataset Analysis notebook is responsible for the formal preparation of the project input data.

Key rules include:

- restrict records to calendar year 2025
- retain Route M66
- retain eastbound direction
- retain weekday service
- retain Morning hours 6 to 10 and Evening hours 15 to 19
- retain selected stop sequences 6 to 10 for the modeled corridor
- preserve a separate verified upstream subset for occupancy estimation
- check nulls, duplicates, invalid/negative counts, source-absent combinations, and cross-source mapping consistency
- do not delete a high observation solely because it appears extreme
- do not automatically fill source-absent combinations with zero

The cleaned selected-stop dataset is saved as:

```text
MODESIM_Project/data/processed/MTA_M66_Selected_Stops_2025_CLEAN.csv
```

## 8. Representative Passenger Demand

For each selected stop-hour combination, representative boarding demand is derived from the cleaned historical data.

The simulation converts representative boarding values into non-negative whole passenger counts using deterministic rounding:

```text
Passenger Count = max(0, floor(Boardings + 0.5))
```

Each virtual passenger is then assigned an arrival time within the corresponding hour using the project random-number stream.

Baseline and corresponding scenario comparisons use reproducible seeds so matched alternatives can be evaluated under compatible stochastic demand realizations.

## 9. Passenger Arrival Process

Within each modeled stop-hour, individual passenger arrival times are generated across the hour using a uniform within-hour arrival assumption.

This is a modeling assumption, not a claim that actual M66 passenger arrivals are uniformly distributed throughout every hour.

Passenger records retain the fields needed for matched simulation, including replication identity, seed, passenger identity, stop sequence, hour, period, and arrival time.

## 10. Bus Service Representation

### 10.1 Reference service

Baseline and High-Demand reference simulations use the verified published GTFS service.

Reference buses use the exact retained GTFS arrival times at the five modeled stops.

### 10.2 Candidate GA service

GA candidates do not reproduce exact GTFS departure times. Instead, the optimizer selects integer trip counts for the five study hours in one period.

For a candidate allocation:

1. candidate buses at Stop 6 are evenly spaced within each hour using midpoint spacing;
2. downstream candidate arrival times are produced by adding the hour-specific median GTFS travel offset from Stop 6 to each downstream modeled stop;
3. starting occupancy is recalculated from the same underlying hourly upstream net-flow information and the candidate number of buses;
4. stop-hour alighting targets are redistributed across the candidate buses while preserving the whole target.

## 11. Initial Bus Occupancy

The model estimates passengers already onboard before the first selected stop using the verified upstream ridership subset.

For each study hour, representative upstream net passenger flow is allocated across the eligible buses serving that hour.

For candidate GA schedules, the same underlying hourly upstream flow is redistributed across the candidate number of buses rather than copied from the reference trip-level occupancy values.

Initial occupancy is bounded by the modeled passenger capacity.

## 12. Alighting Allocation

Representative stop-hour alighting demand is converted to a whole-number target and distributed across eligible buses using a deterministic quotient-and-remainder procedure.

The procedure preserves the complete stop-hour alighting target while producing whole-number per-bus assignments.

At a bus arrival event, alighting is processed before boarding.

## 13. Discrete-Event Simulation Logic

The system is a terminating discrete-event queueing simulation.

Main entity/event types:

- passenger arrival
- bus arrival

Main state information includes:

- simulation clock
- FIFO queue at each modeled stop
- passenger queue-entry time
- current bus occupancy
- assigned alighting count
- boarded passenger records
- waiting-time records
- queue-length history
- occupancy history
- final waiting passengers

### 13.1 Passenger arrival event

When a passenger arrival event is processed:

1. the simulation clock advances to the event time;
2. the passenger is added to the FIFO queue of the assigned stop;
3. queue state is updated for later metric calculation.

### 13.2 Bus arrival event

When a bus arrives at a modeled stop:

1. scheduled alightings are applied first;
2. the remaining available capacity is calculated;
3. passengers board from the front of the FIFO queue until either the queue is empty or available capacity is exhausted;
4. completed passenger waiting times are recorded;
5. bus occupancy and queue state are updated.

### 13.3 Exact-time event priority

If a passenger and a bus have the exact same event time, the bus event is processed first.

The event queue therefore uses bus priority before passenger priority for an exact timestamp tie.

## 14. Capacity Rule

All simulated buses use a modeled passenger capacity of:

```text
60 passengers
```

The value is a project modeling assumption used to enforce capacity-limited boarding. It should not be interpreted as a claim that every physical M66 vehicle has an identical certified maximum capacity of exactly 60 passengers.

## 15. Simulation Termination and Backlog

Passenger generation stops at the defined study-period boundary.

Eligible buses are allowed to complete their remaining modeled stop events. The model does not add unlimited extra service after the last eligible bus.

Two related queue measures are retained:

- **Period-End Queue:** passengers waiting at the official study-period boundary.
- **Final Backlog:** passengers still waiting after the last eligible bus has completed its modeled service.

These measures can differ because buses scheduled after the official boundary may still serve passengers who arrived before the boundary.

## 16. Performance Metrics

The main simulation metrics are:

- mean completed passenger waiting time
- 95th percentile completed passenger waiting time
- peak queue
- period-end queue
- final backlog
- mean bus occupancy
- maximum bus occupancy
- passenger conservation

Completed-passenger waiting metrics do not include passengers who remain unserved. For that reason, waiting-time improvement is interpreted together with final backlog rather than by itself.

## 17. Scenario Definitions

| Scenario | Selected-stop passenger demand | Reference service condition | Upstream occupancy/alighting treatment |
|---|---|---|---|
| Baseline | Baseline representative demand | Published GTFS reference service | Baseline inputs |
| High-Demand | +40% selected-stop boarding demand | Published GTFS reference service | Baseline upstream occupancy and alighting targets remain unchanged |
| Reduced-Service | Baseline selected-stop demand | One reference trip removed from each study hour | Occupancy and alighting assignments are recomputed for the remaining buses |
| Combined | High-Demand passenger streams | Reduced-Service condition | Reduced-Service-side occupancy/alighting treatment; these inputs are not multiplied by 1.40 |

### 17.1 High-Demand rounding

The High-Demand whole-number passenger target is derived from the unrounded representative boarding value before deterministic rounding.

Conceptually:

```text
High-Demand Count = max(0, floor(1.40 × representative Boardings + 0.5))
```

The High-Demand generator preserves the complete Baseline passenger stream and creates only the additional passengers needed to reach the increased target. This supports common-random-number comparison with Baseline.

### 17.2 Reduced-Service removal rule

Reduced-Service removes one reference trip from each study hour.

The removal is deterministic:

- identify the eligible reference trip at Stop 6 whose scheduled arrival is closest to the midpoint of the hour;
- use the earlier trip as the tie-breaker if two trips are equally close;
- remove the same `trip_id` consistently across the five modeled stops.

This produces fixed Reduced-Service period budgets of:

- Morning: 38 trips
- Evening: 39 trips

## 18. AI Role and Technique Selection

The final AI role is **simulation-based service optimization**.

During the Midterm phase, three optimization techniques were screened under a common evaluation design:

- Genetic Algorithm (GA)
- Simulated Annealing (SA)
- Particle Swarm Optimization (PSO)

GA was selected for the succeeding project phase.

The final GA does not predict passenger demand. Instead, it proposes hourly service allocations and receives simulation-based performance as its evaluation signal.

## 19. GA Decision Variable and Service Budgets

Each GA plan is a five-element integer vector representing hourly trip counts for one Morning or Evening study period.

Scenario-specific constraints:

| Scenario | Morning budget | Evening budget | Hourly bounds |
|---|---:|---:|---:|
| Baseline | 43 | 44 | 5 to 12 |
| High-Demand | 43 | 44 | 5 to 12 |
| Reduced-Service | 38 | 39 | 4 to 12 |
| Combined | 38 | 39 | 4 to 12 |

The 4-trip lower bound for Reduced-Service and Combined includes the minimum hourly service present in the defined Reduced-Service reference condition.

The 12-trip upper bound retains the highest hourly service level observed in the verified original GTFS study-period service.

Scenario severity for Reduced-Service and Combined is controlled primarily by the fixed 38/39 period budgets, while the GA is allowed to redistribute those totals across the five hours within the 4-to-12 range.

## 20. GA Search and Selection Design

Current GA configuration:

- search replications: first 5 matched validation replications
- optimizer seeds: 101, 202, 303
- unique service-plan evaluation budget per optimizer run: 10
- final validation: full matched validation-replication set

The search objective is based on mean completed passenger waiting time subject to feasibility constraints.

### 20.1 Final-backlog safeguard

A candidate cannot be selected only because it improves completed-passenger waiting time while leaving more passengers unserved.

For each scenario and study period, the selected plan must have mean final backlog no worse than the corresponding non-optimized reference service evaluated on the matched validation set.

A plan that violates the required backlog safeguard is treated as infeasible for selection.

## 21. Common Random Numbers and Matched Comparisons

The experiment uses reproducible random-number streams and matched replications where applicable.

Important principles:

- a master seed generates reproducible replication seeds;
- corresponding alternatives use matched passenger-stream realizations whenever the comparison design requires them;
- High-Demand preserves Baseline passengers and adds only the incremental demand;
- reference and optimized results are compared using matched replication identifiers.

This reduces unnecessary stochastic noise in direct paired comparisons.

## 22. Replications and Precision Rule

Scenario experiments begin with:

```text
30 replications
```

Precision is assessed using 95% confidence intervals for the designated primary metrics in both study periods.

If the required precision is not met, the Scenario experiment can extend the number of replications in batches of 10 up to a maximum of 50.

The implemented precision rule uses a relative half-width criterion where appropriate and an absolute threshold for metrics whose mean is small.

The GA notebook separately checks the precision of selected-plan results on the available matched validation replications.

## 23. Validation Rules

The implementation uses explicit checks rather than relying only on visual inspection of results.

Main validation categories include:

- required input files exist
- study hours match the configured hours
- modeled stop sequences match the configured stops
- passenger conservation
- bus occupancy does not exceed modeled capacity
- service-plan budget preservation
- hourly service-plan bounds
- High-Demand multiplier construction
- Reduced-Service removed-trip rule
- replication/seed alignment
- Baseline reproduction in the generalized GA implementation
- final-backlog safeguard
- stop-level output structure
- expected output-file creation

Validation failures should stop execution or be surfaced clearly rather than being silently ignored.

## 24. Key Data Contracts

The following table lists the most important cross-notebook files. It is not an exhaustive list of every reviewer-facing CSV.

| Producer | File | Main consumer / purpose |
|---|---|---|
| Dataset Analysis | `data/processed/MTA_M66_Selected_Stops_2025_CLEAN.csv` | Main selected-stop demand input for simulation notebooks |
| Dataset Analysis | `output/tables/gtfs_selected_stop_mapping.csv` | Reproducibility evidence for selected-stop GTFS mapping |
| Dataset Analysis | `output/tables/gtfs_upstream_stop_mapping.csv` | Reproducibility evidence for upstream mapping |
| Baseline Simulation | `data/processed/M66_Replication_Seeds.csv` | Shared replication-seed evidence |
| Baseline Simulation | `data/processed/M66_Master_Passenger_Streams_30_Replications.csv` | Reproducible Baseline passenger streams |
| Baseline Simulation | `data/processed/M66_Baseline_30_Replications.csv` | Baseline reference replication results |
| Baseline Simulation | `data/processed/M66_Baseline_Precision_Check.csv` | Baseline precision evidence |
| Scenario Simulation | `data/processed/M66_HighDemand_Master_Passenger_Streams.csv` | High-Demand and Combined GA passenger streams |
| Scenario Simulation | `data/processed/M66_HighDemand_Results.csv` | High-Demand reference results |
| Scenario Simulation | `data/processed/M66_ReducedService_Results.csv` | Reduced-Service reference results |
| Scenario Simulation | `data/processed/M66_Combined_Results.csv` | Combined reference results |
| Scenario Simulation | `data/processed/M66_ReducedService_Service_Plan.csv` | Reduced-Service reference service-plan definition |
| GA Optimization | `output/tables/ga_scenario_selected_plan_replications.csv` | Full selected-plan replication-level results |
| GA Optimization | `output/tables/ga_scenario_paired_reference_vs_ga.csv` | Paired reference-versus-GA comparison with confidence intervals |
| GA Optimization | `output/tables/ga_scenario_safeguards_check.csv` | Final-backlog safeguard evidence |
| GA Optimization | `output/tables/ga_scenario_validation_summary.csv` | Selected-plan validation evidence |

## 25. Output Ownership

### 25.1 Dataset Analysis outputs

Typical ownership prefixes / subjects:

- filtering summary
- data-quality summary
- source-absence summary
- stop ID history
- GTFS mappings
- stop/hour/period demand summaries
- demand and service figures

### 25.2 Baseline Simulation outputs

Typical ownership prefixes / subjects:

- Baseline replication outputs
- Baseline precision checks
- GA/SA/PSO technique-screening outputs
- selected AI service plans
- Baseline optimized-versus-GTFS paired comparison
- Midterm AI screening figures

### 25.3 Scenario Simulation outputs

Current scenario outputs use the `scenario_...` naming family for reviewer-facing tables and include three current figures:

```text
scenario_comparison_summary.png
stop_level_peak_queue_morning.png
stop_level_peak_queue_evening.png
```

The notebook also generates `scenario_output_manifest.csv`, which is the authoritative list of current Scenario-generated review files.

### 25.4 GA Optimization outputs

Current GA reviewer-facing outputs use the `ga_...` / `ga_scenario_...` naming family.

The notebook generates `ga_output_manifest.csv`, which is the authoritative list of current GA-generated review files.

The Scenario and GA output manifests identify the current generated review files for those notebooks.


## 26. Environment and Reproducibility

The repository targets Python 3.12.

Required top-level packages are listed in the repository root `requirements.txt`.

The current dependency set includes:

- NumPy
- pandas
- Matplotlib
- SciPy
- JupyterLab
- ipykernel

Recommended environment workflow:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name m66-passenger-queue-simulation --display-name "M66 Passenger Queue Simulation"
```

Run Jupyter from:

```powershell
cd MODESIM_Project\code
jupyter lab
```

Use the same project kernel for all four notebooks.

The repository root `requirements.txt` defines the Python packages required to run the notebooks. The same Python 3.12 project environment should be used across all four notebooks.

## 27. Interpretation Limits

The project is a controlled simulation and service-allocation study, not a reconstruction of one historical operating day.

Important limitations include:

- APC observations may not represent complete ridership activity because APC coverage can be incomplete.
- Source-absent combinations are ambiguous and are not automatically zero-filled.
- Historical 2025 ridership and the frozen current GTFS schedule represent different time periods.
- The model covers only five consecutive eastbound M66 stops rather than the entire route.
- Bus arrivals are scheduled GTFS events, not observed real-time arrivals.
- The implementation does not reconstruct actual traffic delay, bunching, cancellation, early running, or detailed dwell-time variability.
- Uniform within-hour passenger arrivals are a simulation assumption.
- The 60-passenger capacity is a project modeling assumption.
- Completed-passenger waiting time can look favorable even when unserved passengers remain, so final backlog must be interpreted alongside waiting metrics.
- GA results are search results under the defined evaluation budget and are not presented as mathematical proof of a global optimum.

Simulation and optimization outputs therefore require human interpretation before any real service-planning use.

## 28. Technical and Methodological Sources

| Source | Used for |
|---|---|
| MTA Bus Stop Level Ridership: Beginning 2024, https://data.ny.gov/d/fvdm-uavx | Historical passenger-demand, alighting, upstream-load, and data-quality inputs |
| MTA Developer Resources, https://www.mta.info/developers | Frozen Manhattan static GTFS service input |
| GTFS Schedule Reference, https://gtfs.org/documentation/schedule/reference/ | Interpretation of GTFS schedule fields |
| pandas documentation, https://pandas.pydata.org/docs/ | Data loading, grouping, transformations, and exports |
| NumPy documentation, https://numpy.org/doc/ | Random-number generation and numerical operations |
| SciPy `scipy.stats.t` documentation, https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.t.html | Student-t critical values used in confidence-interval calculations |
| Python `heapq` documentation, https://docs.python.org/3/library/heapq.html | Chronological discrete-event priority queue implementation |
| Oliveira et al. (2024), Applied Soft Computing, https://doi.org/10.1016/j.asoc.2024.111578 | Methodological background for GA-based bus service/frequency allocation with service constraints and waiting-time-oriented evaluation |
| Gkiotsalitis (2020), IET Intelligent Transport Systems, https://doi.org/10.1049/iet-its.2019.0725 | Methodological background for headway/service scheduling and passenger waiting-time considerations |
| Law, A. M. (2024), *Simulation Modeling and Analysis* (6th ed.) | Independent replications, uncertainty analysis, and confidence-interval methodology |

