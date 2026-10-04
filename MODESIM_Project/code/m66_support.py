#shared checks keep the notebooks on the same rules
import numpy as np
import pandas as pd
from scipy.stats import t


PASSENGER_COLUMNS = [
    "Stop Sequence", "Stop Name", "Hour", "Period", "Arrival Minutes"
]


def finite_replications(values):
    #pandas skips missing values, so check them before counting replications
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or len(values) < 2:
        raise ValueError("Use at least two replication values.")
    if not np.isfinite(values).all():
        raise ValueError("A replication metric is missing or not finite.")
    return values


def validate_demand(demand):
    #a fractional count must not disappear through an int conversion
    required = {"Stop Sequence", "Stop Name", "Hour", "Passenger Count"}
    if not required.issubset(demand.columns):
        raise ValueError("The demand table is missing required columns.")
    counts = pd.to_numeric(demand["Passenger Count"], errors="raise").to_numpy()
    if not np.isfinite(counts).all() or (counts < 0).any():
        raise ValueError("Passenger counts must be finite and nonnegative.")
    if not np.equal(counts, np.floor(counts)).all():
        raise ValueError("Passenger counts must be whole numbers.")
    if demand.duplicated(["Stop Sequence", "Hour"]).any():
        raise ValueError("The demand table repeats a stop-hour cell.")


def allocate_initial_occupancy(schedule, upstream_flow, capacity=60):
    #round the hourly target once so changing the bus count cannot change demand
    required = {"trip_id", "Hour", "Period"}
    if not required.issubset(schedule.columns):
        raise ValueError("The schedule is missing trip, hour, or period columns.")
    if schedule["trip_id"].isna().any() or schedule["trip_id"].duplicated().any():
        raise ValueError("Every scheduled bus needs a unique trip id.")
    if isinstance(capacity, bool) or not np.isfinite(capacity) or capacity < 1 or int(capacity) != capacity:
        raise ValueError("Capacity must be a positive whole number.")
    capacity = int(capacity)
    result = schedule[["trip_id", "Hour", "Period"]].copy()
    result["Initial Occupancy"] = 0
    for hour, group in result.groupby("Hour", sort=True):
        flow = float(upstream_flow[hour])
        if not np.isfinite(flow):
            raise ValueError("An upstream hourly flow is not finite.")
        target = int(np.floor(max(0.0, flow) + 0.5))
        #do not hide upstream passengers when the schedule cannot carry them
        if target > len(group) * capacity:
            raise ValueError(f"Hour {hour} cannot carry upstream target {target}.")
        quotient, remainder = divmod(target, len(group))
        #use trip id order to break ties in a way that survives dataframe shuffling
        order = group.sort_values("trip_id", kind="stable").index
        result.loc[order, "Initial Occupancy"] = [
            quotient + (position < remainder)
            for position in range(len(group))
        ]
        if int(result.loc[group.index, "Initial Occupancy"].sum()) != target:
            raise AssertionError("The upstream hourly target changed.")
    result["Initial Occupancy"] = result["Initial Occupancy"].astype(int)
    return result


def paired_difference(reference, candidate, metric, keys=None):
    #match each random passenger realization before comparing service plans
    keys = keys or ["Replication", "Seed", "Period"]
    for frame in (reference, candidate):
        if not set(keys + [metric]).issubset(frame.columns):
            raise ValueError("A paired comparison is missing required columns.")
        if frame[keys].isna().any().any() or frame.duplicated(keys).any():
            raise ValueError("Paired keys must be present and unique.")
    left_keys = set(map(tuple, reference[keys].to_numpy()))
    right_keys = set(map(tuple, candidate[keys].to_numpy()))
    if left_keys != right_keys:
        raise ValueError("Reference and candidate replication keys differ.")
    joined = reference[keys + [metric]].merge(
        candidate[keys + [metric]], on=keys, validate="one_to_one",
        suffixes=("_Reference", "_Candidate")
    )
    left = finite_replications(joined[f"{metric}_Reference"])
    right = finite_replications(joined[f"{metric}_Candidate"])
    #negative differences mean the candidate has a smaller metric
    delta = right - left
    half_width = float(t.ppf(0.975, len(delta) - 1) * delta.std(ddof=1) / np.sqrt(len(delta)))
    mean = float(delta.mean())
    return {
        "Metric": metric, "Replications": len(delta),
        "Reference Mean": float(left.mean()), "Candidate Mean": float(right.mean()),
        "Paired Difference": mean, "Difference CI Lower": mean - half_width,
        "Difference CI Upper": mean + half_width,
        "Reduction Supported": bool(mean + half_width < 0)
    }
