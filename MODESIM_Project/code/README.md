# Project code

Run these notebooks from the first cell in order, using a fresh kernel for each:

1. `m66_dataset_analysis.ipynb`: data cleaning and demand analysis.
2. `m66_baseline_simulation.ipynb`: baseline simulation and technique comparison.
3. `m66_scenario_simulation.ipynb`: high-demand, reduced-service, and combined scenarios.
4. `m66_ga_optimization.ipynb`: GA search and independent comparisons.

Use this folder as the notebooks' working directory. Keep the shared modules beside them:

- `m66_core.py`: passenger generation and the event engine.
- `m66_support.py`: load allocation, input checks, and paired comparisons.
- `m66_evaluation.py`: frozen-plan evaluation and service controls.

`run_all.py` runs the notebooks in order and calls `plot_results.py` for the extra comparison figures. Its notebook outputs are plain text. Run in JupyterLab for notebook exports with displayed tables and plots.

See the [root README](../../README.md) for setup, commands, model assumptions, and PDF export steps. See the [technical documentation](../docs/TECHNICAL_DOCUMENTATION.md) for the simulation and experiment rules.
