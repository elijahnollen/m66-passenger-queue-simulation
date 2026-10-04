#run from any folder with python path/to/MODESIM_Project/code/run_all.py
import ast
import contextlib
import csv
import hashlib
import importlib.metadata
import io
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

os.environ.setdefault("MPLBACKEND", "Agg")
CODE_DIR = Path(__file__).resolve().parent
NOTEBOOKS = [
    "m66_dataset_analysis.ipynb", "m66_baseline_simulation.ipynb",
    "m66_scenario_simulation.ipynb", "m66_ga_optimization.ipynb"
]


def run_notebook(path):
    #each notebook gets fresh variables just like a restarted kernel
    notebook = json.loads(path.read_text(encoding="utf-8"))
    namespace = {"__name__": "__main__", "__file__": str(path)}
    count = 0
    for cell_number, cell in enumerate(notebook["cells"], 1):
        if cell["cell_type"] != "code":
            continue
        count += 1
        source = "".join(cell["source"])
        output = io.StringIO()
        print(f"{path.name}: cell {cell_number}", flush=True)
        try:
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                tree = ast.parse(source, filename=f"{path.name}:cell{cell_number}")
                #show the last expression without running any statement twice
                expression = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
                exec(compile(tree, path.name, "exec"), namespace)
                if expression is not None:
                    value = eval(compile(ast.Expression(expression.value), path.name, "eval"), namespace)
                    if value is not None:
                        print(value)
        except Exception:
            #the old notebook stays untouched if a cell fails
            print(output.getvalue(), file=sys.stderr)
            raise
        cell["execution_count"] = count
        cell["outputs"] = []
        if output.getvalue():
            cell["outputs"].append({"output_type": "stream", "name": "stdout", "text": output.getvalue().splitlines(keepends=True)})
    #write the executed notebook only after every code cell has passed
    path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    os.chdir(CODE_DIR)
    sys.path.insert(0, str(CODE_DIR))
    tables = CODE_DIR.parent / "output" / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    timing_path = tables / "execution_runtime.csv"
    #clear the previous timing record so a failed run cannot look complete
    timing_path.unlink(missing_ok=True)
    measured = []
    started = perf_counter()
    #each notebook checks its inputs and model rules while it runs
    for name in NOTEBOOKS:
        stage_started = perf_counter()
        run_notebook(CODE_DIR / name)
        measured.append((name, perf_counter() - stage_started))
    #draw the extra comparison figures from the tables saved by the ga notebook
    stage_started = perf_counter()
    subprocess.run([sys.executable, str(CODE_DIR / "plot_results.py")], check=True)
    measured.append(("plot_results.py", perf_counter() - stage_started))
    measured.append(("Full sequential run", perf_counter() - started))
    #record the machine with the measured times rather than promise a fixed runtime
    cpu = platform.processor()
    if Path("/proc/cpuinfo").exists():
        cpu = next((line.split(":", 1)[1].strip() for line in Path("/proc/cpuinfo").read_text().splitlines() if line.startswith("model name")), cpu)
    memory_gib = None
    try:
        memory_gib = round(os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE") / 1024 ** 3, 2)
    except (ValueError, OSError, AttributeError):
        pass
    #hash code cells and modules without notebook outputs, which change during a run
    digest = hashlib.sha256()
    for path in sorted(CODE_DIR.iterdir()):
        if path.suffix == ".py":
            digest.update(path.name.encode()); digest.update(path.read_bytes())
        elif path.suffix == ".ipynb":
            notebook = json.loads(path.read_text(encoding="utf-8"))
            digest.update(path.name.encode())
            for cell in notebook["cells"]:
                if cell["cell_type"] == "code":
                    digest.update("".join(cell["source"]).encode())
    metadata = {
        "Measured UTC": datetime.now(timezone.utc).isoformat(),
        "Python": platform.python_version(), "Platform": platform.platform(),
        "CPU": cpu, "Logical CPUs": os.cpu_count(), "Host Memory GiB": memory_gib,
        "Packages": "; ".join(f"{name}={importlib.metadata.version(name)}" for name in ["numpy", "pandas", "scipy", "matplotlib"]),
        "Code SHA256": digest.hexdigest()
    }
    with timing_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["Stage", "Seconds", "Minutes", *metadata])
        writer.writeheader()
        for name, seconds in measured:
            writer.writerow({"Stage": name, "Seconds": round(seconds, 6), "Minutes": round(seconds / 60, 6), **metadata})
            print(f"{name}: {seconds:.1f} seconds", flush=True)
    print("All four notebooks completed and comparison figures were saved.")


if __name__ == "__main__":
    main()
