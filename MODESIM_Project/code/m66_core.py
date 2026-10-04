#one event engine is shared by baseline, scenarios, and ga
#the project keeps the five stops and capacity fixed across these notebooks
import heapq
import numpy as np
import pandas as pd
from scipy.stats import t
from m66_support import PASSENGER_COLUMNS, finite_replications, validate_demand

selected_stops = [6, 7, 8, 9, 10]
bus_capacity = 60
precision_confidence_level = 0.95

def handle_passenger_arrival(
    event_time,
    stop_sequence,
    passenger_id,
    stop_queues,
    queue_history,
    peak_queue,
    peak_queue_time
):
    #add one passenger-arrival event to the fifo queue for the matching modeled stop.
    stop_queues[stop_sequence].append(
        (passenger_id, event_time)
    )

    current_queue = len(stop_queues[stop_sequence])

    #record the updated queue length after the passenger joins.
    queue_history.append({
        "Time": event_time,
        "Stop Sequence": stop_sequence,
        "Queue Length": current_queue,
        "Event": "passenger_arrival"
    })

    #update the stop-level peak queue and the time when it occurs.
    if current_queue > peak_queue[stop_sequence]:
        peak_queue[stop_sequence] = current_queue
        peak_queue_time[stop_sequence] = event_time

def handle_bus_arrival(
    event_time,
    stop_sequence,
    trip_id,
    stop_queues,
    bus_occupancy,
    waiting_records,
    queue_history,
    bus_history,
    occupancy_lookup,
    service_alighting_lookup,
    capacity=bus_capacity
):
    #set up the bus occupancy when the trip first enters the
    #modeled five-stop segment.
    #process one bus arrival using alighting-before-boarding logic and the modeled capacity limit.
    #check counts before converting them to integers
    raw_load = occupancy_lookup[trip_id]
    raw_alightings = service_alighting_lookup[(trip_id, stop_sequence)]
    for count in (raw_load, raw_alightings):
        if isinstance(count, (bool, np.bool_)) or not np.isfinite(count) or count < 0 or int(count) != count:
            raise ValueError("Bus loads and alightings must be nonnegative whole numbers.")
    if raw_load > capacity:
        raise ValueError("The starting bus load exceeds capacity.")
    if trip_id not in bus_occupancy:
        bus_occupancy[trip_id] = int(
            occupancy_lookup[trip_id]
        )

    occupancy_before = bus_occupancy[trip_id]

    #retrieve the number of passengers assigned to alight at this
    #trip and stop.
    assigned_alightings = int(
        service_alighting_lookup[(trip_id, stop_sequence)]
    )

    #prevent alightings from exceeding the passengers currently onboard.
    actual_alightings = min(
        assigned_alightings,
        bus_occupancy[trip_id]
    )

    #apply alightings before calculating the capacity available
    #for waiting passengers.
    bus_occupancy[trip_id] -= actual_alightings

    available_capacity = capacity - bus_occupancy[trip_id]

    #board passengers in fifo order up to the remaining bus capacity.
    boarded = min(
        len(stop_queues[stop_sequence]),
        available_capacity
    )

    for _ in range(boarded):
        passenger_id, passenger_arrival = stop_queues[
            stop_sequence
        ].pop(0)

        waiting_time = event_time - passenger_arrival

        waiting_records.append({
            "Passenger ID": passenger_id,
            "Stop Sequence": stop_sequence,
            "Trip ID": trip_id,
            "Passenger Arrival": passenger_arrival,
            "Boarding Time": event_time,
            "Waiting Time": waiting_time
        })

    bus_occupancy[trip_id] += boarded

    remaining_queue = len(stop_queues[stop_sequence])

    #record the queue state after the bus finishes boarding.
    queue_history.append({
        "Time": event_time,
        "Stop Sequence": stop_sequence,
        "Queue Length": remaining_queue,
        "Event": "bus_arrival"
    })

    #record the occupancy and boarding activity for validation
    #and output metrics.
    bus_history.append({
        "Trip ID": trip_id,
        "Stop Sequence": stop_sequence,
        "Time": event_time,
        "Occupancy Before": occupancy_before,
        "Assigned Alightings": assigned_alightings,
        "Actual Alightings": actual_alightings,
        "Boarded": boarded,
        "Occupancy After": bus_occupancy[trip_id],
        "Passengers Left Waiting": remaining_queue
    })

def create_period_event_queues(
    passengers,
    service_stop_times,
    trip_period_lookup_table
):
    #build chronological morning and evening event queues for the supplied passenger stream and service plan.
    if not passengers["Period"].isin(["Morning", "Evening"]).all():
        raise ValueError("A passenger has an unknown study period.")
    if not set(trip_period_lookup_table.values()).issubset({"Morning", "Evening"}):
        raise ValueError("A trip has an unknown study period.")
    morning_events = []
    evening_events = []

    #add passenger-arrival events to the appropriate study period.
    for _, passenger in passengers.iterrows():
        event = (
            float(passenger["Arrival Minutes"]),
            1,
            "passenger_arrival",
            int(passenger["Stop Sequence"]),
            passenger["Passenger ID"]
        )

        if passenger["Period"] == "Morning":
            heapq.heappush(morning_events, event)
        else:
            heapq.heappush(evening_events, event)

    #add scheduled bus-arrival events using the service inputs
    #supplied for the current scenario.
    for _, bus in service_stop_times.iterrows():
        event = (
            float(bus["arrival_minutes"]),
            0,
            "bus_arrival",
            int(bus["stop_sequence"]),
            bus["trip_id"]
        )

        if (
            trip_period_lookup_table[bus["trip_id"]]
            == "Morning"
        ):
            heapq.heappush(morning_events, event)
        else:
            heapq.heappush(evening_events, event)

    return morning_events, evening_events

def run_service_simulation(
    period,
    events,
    generated_passengers,
    replication,
    seed,
    occupancy_lookup,
    service_alighting_lookup
):
    #define the official boundaries of the requested study period.
    #run the event-driven queue simulation for one study period and return performance, history, and validation outputs.
    if period not in {"Morning", "Evening"}:
        raise ValueError("Unknown study period.")
    if period == "Morning":
        start_time = 6 * 60
        end_time = 11 * 60
    else:
        start_time = 15 * 60
        end_time = 20 * 60

    #copy the event list so the original scenario event queues are
    #not modified during the simulation run.
    simulation_events = events.copy()
    heapq.heapify(simulation_events)

    #set up the simulation state for queues, buses, and histories.
    stop_queues = {
        stop: []
        for stop in selected_stops
    }

    bus_occupancy = {}
    waiting_records = []
    queue_history = []
    bus_history = []

    peak_queue = {
        stop: 0
        for stop in selected_stops
    }

    peak_queue_time = {
        stop: None
        for stop in selected_stops
    }

    simulation_clock = start_time
    period_end_queue = None
    period_end_recorded = False

    #record the initial empty queue state at every modeled stop.
    for stop in selected_stops:
        queue_history.append({
            "Time": simulation_clock,
            "Stop Sequence": stop,
            "Queue Length": 0,
            "Event": "simulation_start"
        })

    #process passenger and bus events in chronological order.
    while simulation_events:
        event = heapq.heappop(simulation_events)

        (
            event_time,
            priority,
            event_type,
            stop_sequence,
            event_id
        ) = event

        #capture the queue state at the official end of the study
        #period before processing later events.
        if (
            not period_end_recorded
            and event_time > end_time
        ):
            period_end_queue = {
                stop: len(queue)
                for stop, queue in stop_queues.items()
            }

            period_end_recorded = True

        #bad events must stop the run before they can change a queue
        if not np.isfinite(event_time) or event_time < start_time:
            raise ValueError("An event time is invalid for this period.")
        if stop_sequence not in stop_queues:
            raise ValueError("An event refers to an unmodeled stop.")
        if event_type not in {"passenger_arrival", "bus_arrival"}:
            raise ValueError("Unknown event type.")
        if event_type == "passenger_arrival" and event_time >= end_time:
            raise ValueError("Passenger arrivals must be inside the study period.")
        simulation_clock = event_time

        #apply the appropriate event-processing rule.
        if event_type == "passenger_arrival":
            handle_passenger_arrival(
                event_time,
                stop_sequence,
                event_id,
                stop_queues,
                queue_history,
                peak_queue,
                peak_queue_time
            )
        else:
            handle_bus_arrival(
                event_time,
                stop_sequence,
                event_id,
                stop_queues,
                bus_occupancy,
                waiting_records,
                queue_history,
                bus_history,
                occupancy_lookup,
                service_alighting_lookup,
                capacity=bus_capacity
            )

    #if no event occurred after the official period boundary, use the
    #final queue state as the recorded period-end queue.
    if not period_end_recorded:
        period_end_queue = {
            stop: len(queue)
            for stop, queue in stop_queues.items()
        }

    #passengers still waiting after the final eligible bus form the
    #final backlog for the period.
    final_backlog = {
        stop: len(queue)
        for stop, queue in stop_queues.items()
    }

    #convert recorded simulation histories to dataframes for metric
    #calculation and validation. explicit schemas keep empty results valid.
    waiting_df = pd.DataFrame(
        waiting_records,
        columns=[
            "Passenger ID",
            "Stop Sequence",
            "Trip ID",
            "Passenger Arrival",
            "Boarding Time",
            "Waiting Time",
        ],
    )

    bus_history_df = pd.DataFrame(
        bus_history,
        columns=[
            "Trip ID",
            "Stop Sequence",
            "Time",
            "Occupancy Before",
            "Assigned Alightings",
            "Actual Alightings",
            "Boarded",
            "Occupancy After",
            "Passengers Left Waiting",
        ],
    )

    queue_history_df = pd.DataFrame(
        queue_history,
        columns=[
            "Time",
            "Stop Sequence",
            "Queue Length",
            "Event",
        ],
    )

    completed_passengers = len(waiting_df)
    total_final_backlog = sum(final_backlog.values())

    #check that every generated passenger is either boarded or remains
    #in the final queue.
    passenger_conservation = (
        generated_passengers
        == completed_passengers + total_final_backlog
    )

    #calculate waiting-time metrics only from passengers who successfully board.
    #when nobody boards, completed-passenger wait metrics are undefined.
    if len(waiting_df):
        mean_wait = float(waiting_df["Waiting Time"].mean())
        median_wait = float(waiting_df["Waiting Time"].median())
        p95_wait = float(waiting_df["Waiting Time"].quantile(0.95))
        max_wait = float(waiting_df["Waiting Time"].max())
    else:
        mean_wait = np.nan
        median_wait = np.nan
        p95_wait = np.nan
        max_wait = np.nan

    min_wait = (
        waiting_df["Waiting Time"].min()
        if len(waiting_df)
        else np.nan
    )

    #check that no completed passenger has a negative waiting time.
    waiting_time_valid = (
        bool(
            (
                waiting_df["Waiting Time"] >= 0
            ).all()
        )
        if len(waiting_df)
        else True
    )

    #calculate bus-occupancy limits only when bus events were recorded.
    if len(bus_history_df):
        max_occupancy = int(
            bus_history_df["Occupancy After"].max()
        )

        min_occupancy = int(
            min(
                bus_history_df["Occupancy After"].min(),
                bus_history_df["Occupancy Before"].min()
            )
        )
    else:
        max_occupancy = np.nan
        min_occupancy = np.nan

    #check that bus occupancy remains within the modeled capacity
    #before and after every bus event.
    occupancy_valid = bool(
        bus_history_df[
            "Occupancy After"
        ].between(
            0,
            bus_capacity
        ).all()
        and bus_history_df[
            "Occupancy Before"
        ].between(
            0,
            bus_capacity
        ).all()
    )

    #identify the largest queue observed across the five modeled stops.
    overall_peak_queue = max(
        peak_queue.values()
    )

    if overall_peak_queue > 0:
        overall_peak_stop = max(
            peak_queue,
            key=peak_queue.get
        )

        overall_peak_time = peak_queue_time[
            overall_peak_stop
        ]
    else:
        overall_peak_stop = np.nan
        overall_peak_time = np.nan

    #store the period-level metrics and validation results.
    result = {
        "Replication": int(replication),
        "Seed": int(seed),
        "Period": period,
        "Generated Passengers": int(
            generated_passengers
        ),
        "Completed Passengers": int(
            completed_passengers
        ),
        "Mean Completed Wait": float(
            mean_wait
        ),
        "Median Completed Wait": float(
            median_wait
        ),
        "P95 Completed Wait": float(
            p95_wait
        ),
        "Maximum Completed Wait": float(
            max_wait
        ),
        "Minimum Completed Wait": float(
            min_wait
        ),
        "Peak Queue": int(
            overall_peak_queue
        ),
        "Peak Queue Stop": (
            int(overall_peak_stop)
            if np.isfinite(overall_peak_stop)
            else np.nan
        ),
        "Peak Queue Time": (
            float(overall_peak_time)
            if np.isfinite(overall_peak_time)
            else np.nan
        ),
        "Period-End Queue": int(
            sum(period_end_queue.values())
        ),
        "Final Backlog": int(
            total_final_backlog
        ),
        "Mean Bus Occupancy": float(
            bus_history_df[
                "Occupancy After"
            ].mean()
        ),
        "Maximum Bus Occupancy": max_occupancy,
        "Minimum Bus Occupancy": min_occupancy,
        "Passenger Conservation": bool(
            passenger_conservation
        ),
        "Waiting Time Valid": waiting_time_valid,
        "Bus Occupancy Valid": occupancy_valid
    }

    #calculate the matching queue and waiting-time metrics
    #separately for each modeled stop.
    stop_records = []

    for stop in selected_stops:
        stop_waits = (
            waiting_df.loc[
                waiting_df["Stop Sequence"] == stop,
                "Waiting Time"
            ]
            if len(waiting_df)
            else pd.Series(dtype=float)
        )

        stop_records.append({
            "Replication": int(replication),
            "Seed": int(seed),
            "Period": period,
            "Stop Sequence": stop,
            "Completed Passengers": int(
                len(stop_waits)
            ),
            "Mean Wait": (
                float(stop_waits.mean())
                if len(stop_waits)
                else np.nan
            ),
            "P95 Wait": (
                float(
                    stop_waits.quantile(0.95)
                )
                if len(stop_waits)
                else np.nan
            ),
            "Peak Queue": int(
                peak_queue[stop]
            ),
            "Peak Queue Time": (
                peak_queue_time[stop]
            ),
            "Period-End Queue": int(
                period_end_queue[stop]
            ),
            "Final Backlog": int(
                final_backlog[stop]
            )
        })

    stop_level_df = pd.DataFrame(
        stop_records
    )

    return (
        result,
        waiting_df,
        bus_history_df,
        queue_history_df,
        stop_level_df
    )

def generate_scenario_passengers(
    demand_df,
    seed,
    replication,
    id_prefix="P",
    id_start=1,
    source_label=None
):
    #generate a reproducible passenger stream from a supplied stop-hour demand table.
    #check the count before int() can drop a fractional passenger
    validate_demand(demand_df)
    rng = np.random.default_rng(seed)
    records = []

    #generate passenger arrival times independently within each
    #matching 60-minute study-hour interval.
    for _, row in demand_df.iterrows():
        start_minute = int(row["Hour"]) * 60
        end_minute = start_minute + 60

        arrival_times = rng.uniform(
            start_minute,
            end_minute,
            int(row["Passenger Count"])
        )

        #sort arrivals within the stop-hour cell before adding them
        #to the complete passenger stream.
        for arrival_time in sorted(arrival_times):
            records.append({
                "Stop Sequence": int(
                    row["Stop Sequence"]
                ),
                "Stop Name": row["Stop Name"],
                "Hour": int(row["Hour"]),
                "Period": (
                    "Morning"
                    if row["Hour"] < 12
                    else "Evening"
                ),
                "Arrival Minutes": float(
                    arrival_time
                )
            })

    #keep the columns even when every stop-hour count is zero
    passengers = pd.DataFrame(records, columns=PASSENGER_COLUMNS)

    #assign a unique passenger identifier within the replication.
    passengers.insert(
        0,
        "Passenger ID",
        [
            f"R{replication:02d}_{id_prefix}{i:05d}"
            for i in range(
                id_start,
                id_start + len(passengers)
            )
        ]
    )

    #record the passenger source when a scenario contains more than
    #one independently generated component.
    if source_label is not None:
        passengers["Passenger Source"] = source_label

    return passengers

def generate_high_demand_passengers(
    baseline_demand_df,
    additional_demand_df,
    seed,
    replication
):
    #generate the baseline portion using the same demand table and
    #replication seed used by the baseline scenario.
    #create the high-demand stream by preserving baseline passengers and generating only the additional demand.
    baseline_passengers = generate_scenario_passengers(
        baseline_demand_df,
        seed=seed,
        replication=replication,
        id_prefix="P",
        id_start=1,
        source_label="Baseline"
    )

    #convert the additional-passenger table into the same input
    #structure expected by the general passenger generator.
    extra_demand_df = additional_demand_df[
        [
            "Stop Sequence",
            "Stop Name",
            "Hour",
            "Additional Passenger Count"
        ]
    ].rename(
        columns={
            "Additional Passenger Count":
                "Passenger Count"
        }
    )

    #generate only the additional passengers from a separate,
    #deterministic random sub-stream.
    extra_passengers = generate_scenario_passengers(
        extra_demand_df,
        seed=(seed, 1),
        replication=replication,
        id_prefix="H",
        id_start=1,
        source_label="High-Demand Additional"
    )

    #preserve the complete baseline stream in its original order and
    #append only the additional high-demand passengers.
    return pd.concat(
        [
            baseline_passengers,
            extra_passengers
        ],
        ignore_index=True
    )

def compute_precision_check(results_df):
    #evaluate the project 95% confidence-interval precision rule for the primary metrics.
    precision_records = []
    all_passed = True

    for period in ["Morning", "Evening"]:
        period_results = results_df[
            results_df["Period"] == period
        ]

        for metric in [
            "Mean Completed Wait",
            "Peak Queue"
        ]:
            #a missing replication must not be silently dropped from the interval
            values = pd.Series(finite_replications(period_results[metric]))

            n = len(values)

            if n < 2:
                raise ValueError(
                    "At least two replications are required "
                    "for the precision check."
                )

            mean_value = values.mean()
            std_value = values.std(ddof=1)
            standard_error = (
                std_value / np.sqrt(n)
            )

            #calculate the two-sided student's t confidence interval.
            t_critical = t.ppf(
                precision_confidence_level
                + (
                    1
                    - precision_confidence_level
                ) / 2,
                df=n - 1
            )

            half_width = (
                t_critical
                * standard_error
            )

            #apply the project's absolute or relative precision
            #threshold according to the replication mean.
            if mean_value < 10:
                required_half_width = 1.0
            else:
                required_half_width = (
                    0.10 * mean_value
                )

            passed = (
                half_width
                <= required_half_width
            )

            all_passed = (
                all_passed
                and passed
            )

            precision_records.append({
                "Period": period,
                "Metric": metric,
                "Replications": n,
                "Mean": mean_value,
                "Standard Deviation": std_value,
                "CI Lower": (
                    mean_value - half_width
                ),
                "CI Upper": (
                    mean_value + half_width
                ),
                "Half-Width": half_width,
                "Required Half-Width":
                    required_half_width,
                "Precision Passed": passed
            })

    return (
        pd.DataFrame(
            precision_records
        ),
        all_passed
    )