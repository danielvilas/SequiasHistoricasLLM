# Python script to launch Ciena model inference
# Usage: python 05_launch_ciena.py <ds> <model> <detect|classify>

import sys
import os

from sequias_historicas.CienaLauncher import CienaLauncher

def run_test(ds, model, task):
    print("--------------------------------")
    print (f"Running Ciena model '{model}' on dataset '{ds}' for task '{task}'")
    ciena = CienaLauncher()
    
    output_folder = f"./results/{ds}/{task}/{model}/"
    if os.path.exists(f"./{output_folder}/summary.csv"):
            print(f"Output for model {model} already exists. Skipping...")
            return
    
    ciena_model = f"{task}-{model}"

    ciena.launch(
        model=ciena_model,
        input_folder=f"./data/datasets/{ds}_ds/{task}/json",
        output_folder=output_folder,
    )

def main():
    if len(sys.argv) != 4:
        print("Usage: python 06_launch_ciena.py <ds> <model> <detect|classify>")
        sys.exit(1)

    ds = sys.argv[1]
    model = sys.argv[2]
    task = sys.argv[3]

    if task not in ["detect", "classify"]:
        print("Task must be 'detect' or 'classify'")
        sys.exit(1)

    run_test(ds, model, task)

if __name__ == "__main__":
    main()  