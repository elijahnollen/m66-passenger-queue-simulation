# M66 Project Code

## Main notebooks

- `m66_dataset_analysis.ipynb` cleans, checks, and analyzes the M66 ridership dataset.
- `m66_baseline_simulation.ipynb` runs the baseline discrete-event simulation, completes the 30-replication precision check, compares Genetic Algorithm, Simulated Annealing, and Particle Swarm Optimization, and selects the final AI service-optimization technique from the experiment.

## Recommended run order

1. Run `m66_dataset_analysis.ipynb` if the cleaned dataset needs to be rebuilt.
2. Run `m66_baseline_simulation.ipynb` from top to bottom.

## Main saved outputs

Baseline simulation files are saved in `../data/processed/`.
Tables are saved in `../output/tables/`.
Figures are saved in `../output/figures/`.


