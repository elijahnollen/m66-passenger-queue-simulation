#run from any folder with python path/to/MODESIM_Project/code/run_all.py
import ast
import contextlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

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
    #each notebook checks its inputs and model rules while it runs
    for name in NOTEBOOKS:
        run_notebook(CODE_DIR / name)
    #draw the extra comparison figures from the tables saved by the ga notebook
    subprocess.run([sys.executable, str(CODE_DIR / "plot_results.py")], check=True)
    print("All four notebooks completed and comparison figures were saved.")


if __name__ == "__main__":
    main()
