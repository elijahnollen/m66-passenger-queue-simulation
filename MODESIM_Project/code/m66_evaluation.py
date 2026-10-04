#these checks use new passenger seeds after the chosen plans have been frozen
import copy
import numpy as np
import pandas as pd
from m66_core import create_period_event_queues, generate_high_demand_passengers
from m66_core import generate_scenario_passengers, run_service_simulation
from m66_support import paired_difference


def demand_rule(ctx, period, demand):
    #this simple rule gives more trips to hours with more boarding demand
    hours = [6, 7, 8, 9, 10] if period == "Morning" else [15, 16, 17, 18, 19]
    weights = demand.groupby("Hour")["Passenger Count"].sum().reindex(hours, fill_value=0).to_numpy(dtype=float)
    if weights.sum() == 0:
        weights[:] = 1
    target = weights / weights.sum() * ctx["service_budget"][period]
    plan = np.full(5, ctx["min_hourly_trips"], dtype=int)
    #add one trip at a time without breaking the same ga bounds or budget
    while plan.sum() < ctx["service_budget"][period]:
        available = np.flatnonzero(plan < ctx["max_hourly_trips"])
        if not len(available):
            raise ValueError("The demand rule cannot meet this service budget.")
        chosen = available[np.argmax((target - plan)[available])]
        plan[chosen] += 1
    return tuple(int(x) for x in plan)


def run_review_evaluation(contexts, selected_plans, baseline_demand, additional_demand,
                          reference_services, evaluate_plan, output_dir, master_seed):
    #copy the plans first and never change them after seeing the test results
    frozen = selected_plans[["Scenario", "Period", "Service Plan"]].copy(deep=True)
    if frozen.duplicated(["Scenario", "Period"]).any() or len(frozen) != 8:
        raise ValueError("Freeze one plan for each scenario and period.")
    #90901 was used for an exploratory check before the final search design changed
    test_seeds = np.random.SeedSequence([master_seed, 90902]).generate_state(30)
    seed_table = pd.DataFrame({"Replication": range(1001, 1031), "Seed": test_seeds.astype(np.int64)})
    used_seeds = {int(seed) for ctx in contexts.values() for seed in ctx["seed_lookup"].values()}
    if used_seeds.intersection(seed_table["Seed"]):
        raise ValueError("A test seed was already used for plan selection.")
    seed_table.to_csv(output_dir / "review_holdout_seeds.csv", index=False)
    frozen.to_csv(output_dir / "review_frozen_plans.csv", index=False)
    references, reference_stops, candidates, candidate_stops = [], [], [], []
    comparison_rows, stop_comparison_rows, rule_rows = [], [], []
    for name, original in contexts.items():
        ctx = copy.copy(original)
        ctx["seed_lookup"] = dict(zip(seed_table["Replication"], seed_table["Seed"]))
        ctx["passengers_by_replication"] = {}
        high = name in {"High-Demand", "Combined"}
        for row in seed_table.itertuples(index=False):
            #the high-demand case keeps the exact baseline passengers and adds extras
            if high:
                stream = generate_high_demand_passengers(baseline_demand, additional_demand, int(row.Seed), int(row.Replication))
            else:
                stream = generate_scenario_passengers(baseline_demand, int(row.Seed), int(row.Replication))
            ctx["passengers_by_replication"][int(row.Replication)] = stream
        service = reference_services[name]
        scenario_reference, scenario_stops = [], []
        for replication, passengers in ctx["passengers_by_replication"].items():
            events = create_period_event_queues(passengers, service["stop_times"], service["period_lookup"])
            for period, event_list in zip(["Morning", "Evening"], events):
                result, _, _, queue, stops = run_service_simulation(
                    period, event_list, int((passengers["Period"] == period).sum()),
                    replication, ctx["seed_lookup"][replication], service["occupancy_lookup"], service["alighting_lookup"]
                )
                result["Scenario"] = name
                scenario_reference.append(result)
                scenario_stops.append(stops.assign(Scenario=name))
                if replication == 1001:
                    #keep one full queue trace so period means can be checked against events
                    queue.assign(Scenario=name, Period=period).to_csv(
                        output_dir / f"review_reference_queue_{name.lower()}_{period.lower()}.csv", index=False
                    )
        reference = pd.DataFrame(scenario_reference)
        reference_stop = pd.concat(scenario_stops, ignore_index=True)
        references.append(reference)
        reference_stops.append(reference_stop)
        demand = baseline_demand.copy()
        if high:
            demand["Passenger Count"] = demand["Passenger Count"].to_numpy() + additional_demand["Additional Passenger Count"].to_numpy()
        for period in ["Morning", "Evening"]:
            chosen = frozen.loc[(frozen["Scenario"] == name) & (frozen["Period"] == period), "Service Plan"].iloc[0]
            controls = {
                "GA": tuple(chosen),
                #same hourly counts as gtfs, with the ga timing rule, isolates timing changes
                "Regularized Reference": tuple(ctx["reference_plan_lookup"][period]),
                "Demand Rule": demand_rule(ctx, period, demand)
            }
            period_candidates = {}
            for label, plan in controls.items():
                rule_rows.append({"Scenario": name, "Period": period, "Method": label, "Service Plan": plan})
                reps, stops = evaluate_plan(ctx, period, plan, seed_table["Replication"].tolist())
                for check in ["Passenger Conservation", "Waiting Time Valid", "Bus Occupancy Valid"]:
                    if not reps[check].all():
                        raise AssertionError(f"{name}/{period}/{label} failed {check}.")
                candidates.append(reps.assign(Method=label))
                candidate_stops.append(stops.assign(Method=label))
                period_candidates[label] = reps
                for metric in ["Mean Completed Wait", "P95 Completed Wait", "Peak Queue", "Final Backlog"]:
                    row = paired_difference(reference[reference["Period"] == period], reps, metric)
                    comparison_rows.append(dict(row, Scenario=name, Period=period, Comparison=f"{label} minus Published Reference"))
                #pointwise intervals show stop tradeoffs without claiming every stop improves
                for stop in [6, 7, 8, 9, 10]:
                    left = reference_stop[(reference_stop["Period"] == period) & (reference_stop["Stop Sequence"] == stop)]
                    right = stops[stops["Stop Sequence"] == stop]
                    for metric in ["Mean Wait", "P95 Wait", "Final Backlog"]:
                        row = paired_difference(left, right, metric, ["Replication", "Seed", "Period", "Stop Sequence"])
                        stop_comparison_rows.append(dict(row, Scenario=name, Period=period, Stop=stop, Method=label))
            #this comparison uses identical schedule construction on both sides
            for label in ["Regularized Reference", "Demand Rule"]:
                for metric in ["Mean Completed Wait", "P95 Completed Wait", "Peak Queue", "Final Backlog"]:
                    row = paired_difference(period_candidates[label], period_candidates["GA"], metric)
                    comparison_rows.append(dict(row, Scenario=name, Period=period, Comparison=f"GA minus {label}"))
    reference_all = pd.concat(references, ignore_index=True)
    stress_rows = []
    for name in ["High-Demand", "Reduced-Service", "Combined"]:
        for period in ["Morning", "Evening"]:
            left = reference_all[(reference_all["Scenario"] == "Baseline") & (reference_all["Period"] == period)]
            right = reference_all[(reference_all["Scenario"] == name) & (reference_all["Period"] == period)]
            for metric in ["Mean Completed Wait", "P95 Completed Wait", "Peak Queue", "Final Backlog"]:
                stress_rows.append(dict(paired_difference(left, right, metric), Scenario=name, Period=period))
    exports = {
        "review_holdout_reference_replications.csv": reference_all,
        "review_holdout_reference_stops.csv": pd.concat(reference_stops, ignore_index=True),
        "review_holdout_candidate_replications.csv": pd.concat(candidates, ignore_index=True),
        "review_holdout_candidate_stops.csv": pd.concat(candidate_stops, ignore_index=True),
        "review_holdout_paired_comparisons.csv": pd.DataFrame(comparison_rows),
        "review_holdout_stop_comparisons.csv": pd.DataFrame(stop_comparison_rows),
        "review_holdout_stress_vs_baseline.csv": pd.DataFrame(stress_rows),
        "review_control_plans.csv": pd.DataFrame(rule_rows)
    }
    for filename, frame in exports.items():
        frame.to_csv(output_dir / filename, index=False)
    return exports["review_holdout_paired_comparisons.csv"]
