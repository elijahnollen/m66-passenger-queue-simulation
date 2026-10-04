# Technical documentation

## Scope and input meaning

The model covers eastbound M66 stop sequences 6 through 10. Each weekday morning runs from 06:00 to 11:00, and each evening runs from 15:00 to 20:00. The two periods start with empty queues and run independently.

The cleaned demand comes from 2025 stop-level ridership records. The GTFS snapshot has feed version `gtfs_m_20260611T155328Z` and a June 27 to September 5, 2026 feed window. The simulation uses the checked weekday service pattern. This is a controlled combination of historical boarding demand and a later schedule, not a reconstruction of a specific 2025 day.

The dataset notebook checks route, direction, year, weekdays, selected hours, stop sequences, missing values, duplicates, and GTFS mappings. Historical Stop IDs can change, so stop sequence and checked stop names matter when matching the ridership and schedule sources. Do not join the two datasets using an unchecked Stop ID alone. The selected input has 235 source-absent date-stop-hour combinations and one excluded invalid record. Means use the available valid records; missing combinations are not silently treated as zero demand.

## Passenger arrivals

For each selected stop and hour, the average recorded boarding count is rounded with `floor(max(0, mean) + 0.5)`. A replication keeps that whole count fixed and samples each arrival uniformly within the hour. This is not a Poisson count model. The replications capture arrival-time randomness, not all variation between real operating days.

The generator checks nonnegative, finite, whole passenger counts and unique stop-hour cells. It returns the full passenger schema even when all counts are zero. Passenger IDs identify each passenger within the replication. Replication and seed columns are added when streams are exported.

High demand increases the unrounded selected-stop boarding means by 40 percent before rounding. The original baseline passengers keep their exact IDs and arrival times. Only the extra passengers are sampled from the separate `(seed, 1)` random stream. Upstream flow and alighting targets stay unchanged in this scenario.

## Service and bus loads

The reference uses actual eligible GTFS arrival times. Eligibility and study hour are determined at Stop 6. An eligible trip can reach downstream stops after the official period boundary. No extra trips are added to clear a remaining queue.

Bus capacity is an assumed 60 passengers. The upstream flow is the sum of average upstream boardings minus average upstream alightings for Stops 1 through 5. Negative net flow is clipped to zero. Each hourly target is rounded once, then distributed across that hour's buses using quotient and remainder. This keeps the total upstream count unchanged when the number of buses changes. Trip ID order breaks remainder ties in a repeatable way. If the hourly target exceeds the schedule's total capacity, the model stops instead of hiding the excess passengers.

The average occupancy estimate shown in an hourly summary is not a single load assigned to every bus. Actual per-bus integer loads are in the trip-level occupancy table. Stop-hour alighting targets are also distributed by quotient and remainder. Assigned alightings are limited to the passengers actually onboard at the event.

## Shared event engine

`m66_core.py` is the only event-engine implementation. The baseline notebook wraps its five-result return into a four-result interface. The scenario and GA notebooks also use the stop-level result.

Each stop has a FIFO passenger queue. An event contains its time, priority, event type, stop sequence, and passenger or trip ID. Bus events have priority 0, and passenger events have priority 1. A bus is processed first at an exact-time tie. Alighting happens before boarding. Boarding uses the available capacity and takes passengers from the front of the queue.

The engine records passenger waits, bus loads, and queue lengths after each event. It checks period names, event times, modeled stops, event types, starting bus loads, and alighting counts. Invalid inputs stop the run. The queue list is copied into a heap, so calling the simulation does not consume the caller's event queue.

The period-end snapshot includes bus events exactly at 11:00 or 20:00. It is recorded before later eligible downstream events. Final backlog is the queue left after the final eligible event. These are different measures.

### Last-bus diagnostics

Each stop result records `Last Eligible Bus Time` in minutes from midnight, `Arrivals At Or After Last Bus`, and `Earlier Arrivals Still Unserved`. The last arrival is taken from the eligible bus events at that stop, including downstream events after the official period boundary. An exact-time passenger arrival misses that bus because bus events have priority. If a stop has no bus event, its last-bus time is missing and all its arrivals are counted as unserved with no remaining service.

The two passenger components must add to the final backlog. An earlier passenger still unserved is distinct from a passenger who ever missed a full bus: the latter can board a later bus. The diagnostics do not count every temporary capacity denial or measure unmet real-world demand.

The independent test exports `review_last_bus_diagnostics.csv` with 4,800 rows: four conditions, two periods, four service methods, 30 replications, and five stops. `review_last_bus_summary.csv` contains 160 stop-method summaries with last-bus times and mean backlog components. These are reporting outputs and do not change the objective, plan selection, or event rules.

## Metrics

| Metric | Meaning |
| --- | --- |
| Mean completed wait | Mean wait among passengers who board, in minutes |
| P95 completed wait | The 95th percentile of those completed waits |
| Peak queue | Largest queue at any one modeled stop, not the total across all stops |
| Period-end queue | Sum of stop queues at the official period boundary |
| Final backlog | Sum left waiting after the final eligible event |
| Mean bus occupancy | Average post-event load across recorded bus-stop events |

When nobody boards, completed-wait metrics are missing, not zero. When no bus event exists, occupancy summaries are missing. Empty histories can still pass conservation and state-validity checks. Every passenger must either board or remain in the final backlog. Bus occupancy must stay within 0 to 60 before and after each bus event.

## Scenarios

| Condition | Selected-stop demand | Reference service | Trip budgets |
| --- | --- | --- | --- |
| Baseline | Rounded historical mean | Checked GTFS timings | Morning 43, evening 44 |
| High-Demand | 40 percent growth before rounding | Baseline timings | Morning 43, evening 44 |
| Reduced-Service | Baseline | Remove one whole trip per study hour | Morning 38, evening 39 |
| Combined | High-Demand | Reduced-Service timings | Morning 38, evening 39 |

The removed trip is the one whose Stop 6 arrival is closest to the half-hour, with the earlier arrival breaking a tie. That trip is removed at every modeled stop. Bus loads and alighting assignments are rebuilt for the remaining buses.

## Optimization and controls

The decision is a five-element vector of whole hourly trip counts. Its sum equals the period's fixed trip budget. Baseline and high demand use bounds 5 to 12; reduced service and combined use 4 to 12. Booleans, strings, nonfinite values, and fractional counts are rejected before integer conversion.

Candidate buses are placed at equal midpoint intervals within each hour. Each downstream arrival uses the hour-specific median GTFS travel offset from Stop 6. The candidate shares the same upstream target and stop-hour alighting targets as its reference.

The baseline technique screen gives GA, SA, and PSO the same 10-plan budget and three optimizer seeds. The final GA experiment uses population size 12, optimizer seeds 101, 202, and 303, and the first five matched passenger replications for fitness. Fitness is mean completed wait; an invalid plan, nonfinite objective, or mean final backlog above the matched reference receives infinite fitness. Each seed's searched candidates are checked in search-fitness order on the larger selection set until a candidate passes the unchanged backlog safeguard. Those passing candidates are compared before the final plan is chosen. Both the search minimum and the passing candidate rank are saved.

The final GA search checks 100 unique plans per run and starts with the reference allocation and the simple demand rule. This is still a limited search. The code does not prove a global optimum or broad superiority of GA. The three-technique screen uses population size 6 for GA.

The independent evaluation freezes one plan per scenario and period, then creates 30 unused seeds from `SeedSequence([2026, 90902])`. Replication IDs 1001 through 1030 keep these rows distinct. The code checks that the test seeds did not occur in the selection inputs. The test never changes a plan.

Two controls use the same schedule-building rules as GA:

- The regularized reference keeps the GTFS hourly trip counts, but uses midpoint spacing and median downstream offsets.
- The demand rule allocates trips in proportion to hourly selected-stop boardings, using the same budget and bounds.

GA versus the published reference includes both bus-spacing and hourly-allocation changes. GA versus the regularized reference better isolates allocation. Neither comparison includes traffic or fleet constraints. A fixed trip count is not proof of a fixed fleet or operating cost.

## Confidence intervals and precision

The precision rule starts with 30 replications and checks mean completed wait and peak queue. A two-sided 95 percent Student t interval must have half-width at most 1 when the metric mean is below 10, or at most 10 percent of the mean otherwise. Scenario runs can add 10 replications at a time up to 50. A missing or nonfinite replication metric stops the precision check instead of being silently skipped.

Paired comparisons match Replication, Seed, and Period. Stop comparisons also match Stop Sequence. Both sides must have the same unique, complete keys and finite metric values. A candidate-minus-reference interval entirely below zero supports a lower metric for that comparison. An interval containing zero does not support a clear reduction. Stop intervals are pointwise and are not corrected for many simultaneous comparisons.

The larger set used to choose a final plan is a selection set, including tables whose filenames contain validation. Its intervals are descriptive. Use the independent test for claims about a frozen plan under fresh passenger-arrival realizations. Report test-set backlog and stop-level tradeoffs, including unfavorable results. The test does not independently validate the real-world model assumptions.

## Running the project and output ownership

`run_all.py` runs the dataset, baseline, scenario, and GA notebooks in fresh namespaces. It saves each executed notebook only after every code cell in that notebook succeeds. An error stops the run. After the notebooks finish, it calls `plot_results.py` to draw the independent-test figures from the saved tables.

The script runner captures plain-text outputs and saves figures separately. Use JupyterLab to save notebooks with displayed tables and plots for HTML and PDF export. A run writes to the existing result paths, so preserve any earlier outputs you still need before rerunning. If a run fails, its output folders can contain a mix of earlier and partial results. Resolve the error and complete the notebooks in order before using those results together.

The runner measures wall-clock time with `perf_counter` for each notebook, plotting, and the full sequential execution. It removes any previous `execution_runtime.csv` before starting and saves a new timing record only after all stages succeed. The table contains seconds, minutes, measurement time, package versions, host details, and a SHA256 fingerprint of code cells and Python modules. Notebook outputs are excluded from that fingerprint. Installation and download time are excluded from the measurements. Runtime depends on the machine, resource limits, and other activity; use the measured example in the root README as an estimate rather than a guarantee.

The GA notebook rebuilds scenario references from the same frozen raw and clean inputs. It does not depend on loading every exported scenario CSV. Files with the `review_` prefix belong to the independent-test experiment and contain its plans, seeds, replication results, comparisons, and queue traces.

## Checks and remaining limits

The notebooks and shared modules check passenger conservation, waiting-time validity, bus occupancy, scenario configuration, service budgets, passenger counts, replication precision, paired keys, seed separation, and selected-plan safeguards. Invalid inputs or failed checks stop the relevant calculation. These checks assess the implementation under the model rules; they do not validate the model against measured passenger queues.

The model still needs measured arrival, queue, and bus-run data before operational claims are justified. Historical boarding counts may miss passengers who could not board. Uniform arrivals miss bursts. Deterministic travel offsets miss delays and bunching. A five-stop segment does not capture a complete bus route, vehicle circulation, or dispatch feasibility. Capacity is an assumption that needs route-specific evidence or sensitivity analysis.

The useful contribution is a repeatable way to compare hourly allocations, service-loss scenarios, and stop tradeoffs while keeping the simulated passenger demand and trip budgets explicit. Treat recommendations as candidates for further testing, not deployment instructions.

## Data and software sources

The frozen ridership and GTFS input files identify the empirical sources used by the experiments. The notebooks keep source and API links beside the relevant code. Software API documentation explains the functions used; it does not validate the arrival, capacity, or demand assumptions.
