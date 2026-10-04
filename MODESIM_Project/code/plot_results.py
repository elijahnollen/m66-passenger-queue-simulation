#these plots read the saved independent-test rows instead of rerunning the model
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
TABLES = PROJECT_DIR / "output" / "tables"
FIGURES = PROJECT_DIR / "output" / "figures"
SCENARIOS = ["Baseline", "High-Demand", "Reduced-Service", "Combined"]


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    results = pd.read_csv(TABLES / "review_holdout_paired_comparisons.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
    for ax, period in zip(axes, ["Morning", "Evening"]):
        for label, color, offset in [("Regularized Reference", "#2563eb", -0.12), ("Demand Rule", "#059669", 0.12)]:
            rows = results[(results["Period"] == period) & (results["Metric"] == "Mean Completed Wait") & (results["Comparison"] == f"GA minus {label}")].set_index("Scenario").reindex(SCENARIOS)
            means = rows["Paired Difference"].to_numpy()
            errors = np.vstack([means - rows["Difference CI Lower"].to_numpy(), rows["Difference CI Upper"].to_numpy() - means])
            ax.errorbar(means, np.arange(4) + offset, xerr=errors, fmt="o", capsize=3, color=color, label=label)
        ax.axvline(0, color="#475569", linewidth=1)
        ax.set_title(period)
        ax.set_xlabel("GA minus control mean wait (minutes)")
        ax.set_yticks(range(4), SCENARIOS)
        ax.grid(axis="x", alpha=0.2)
    axes[0].invert_yaxis()
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.94), ncol=2, fontsize=9)
    fig.suptitle("Frozen plans on 30 unused seeds: pointwise 95% paired intervals")
    fig.tight_layout(rect=[0, 0, 1, 0.84])
    fig.savefig(FIGURES / "review_holdout_wait_differences.png", dpi=200)
    plt.close(fig)

    stops = pd.read_csv(TABLES / "review_holdout_stop_comparisons.csv")
    stops = stops[(stops["Method"] == "GA") & (stops["Metric"] == "Mean Wait")]
    grid = stops.pivot(index=["Scenario", "Period"], columns="Stop", values="Paired Difference")
    order = [(scenario, period) for scenario in SCENARIOS for period in ["Morning", "Evening"]]
    grid = grid.reindex(order)
    values = grid.to_numpy()
    bound = max(abs(values.min()), abs(values.max()), 0.01)
    fig, ax = plt.subplots(figsize=(9, 5))
    image = ax.imshow(values, cmap="RdBu_r", vmin=-bound, vmax=bound, aspect="auto")
    ax.set_xticks(range(5), [f"Stop {stop}" for stop in grid.columns])
    ax.set_yticks(range(8), [f"{scenario}: {period}" for scenario, period in order])
    for row in range(8):
        for column in range(5):
            ax.text(column, row, f"{values[row, column]:+.2f}", ha="center", va="center", color="white" if abs(values[row, column]) > 0.6 * bound else "black")
    ax.set_title("Mean stop wait: GA minus published reference\nNegative means lower wait; these cells show means, not significance")
    fig.colorbar(image, ax=ax, label="Difference (minutes)")
    fig.tight_layout()
    fig.savefig(FIGURES / "review_holdout_stop_wait_tradeoffs.png", dpi=200)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for ax, period, boundary in zip(axes, ["Morning", "Evening"], [660, 1200]):
        trace = pd.read_csv(TABLES / f"review_reference_queue_combined_{period.lower()}.csv")
        for stop, rows in trace.groupby("Stop Sequence"):
            rows = rows.sort_values("Time", kind="stable")
            ax.step(rows["Time"] / 60, rows["Queue Length"], where="post", label=f"Stop {stop}")
        ax.axvline(boundary / 60, color="black", linestyle="--", linewidth=1)
        ax.set_title(f"Combined reference: {period}")
        ax.set_xlabel("Time of day (hours)")
        ax.grid(alpha=0.2)
    axes[0].set_ylabel("Passengers waiting")
    axes[1].legend(fontsize=8)
    fig.suptitle("One test realization (replication 1001); dashed line marks the period end")
    fig.tight_layout()
    fig.savefig(FIGURES / "review_reference_queue_combined.png", dpi=200)
    plt.close(fig)
    print("Saved three independent-test figures.")


if __name__ == "__main__":
    main()
