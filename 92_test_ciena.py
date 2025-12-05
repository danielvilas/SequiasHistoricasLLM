from sequias_historicas.CienaLauncher import CienaLauncher
import logging
import sys
import os
#logging.basicConfig(level=logging.DEBUG)

ciena = CienaLauncher()

models = [
    "fastest-no-summary",
    "fastest-summary",
    "efficient-no-summary",
    "efficient-summary",
]

def main():
    if len(sys.argv) != 2:
        print("Usage: python 92_test_ciena.py <test_case>")
        sys.exit(1)
    test_case = sys.argv[1]
    for model in models:
        print(f"Testing Ciena model: {model} for test case: {test_case}")
        if os.path.exists(f"./tests/{test_case}/{model}/summary.csv"):
            print(f"Output for model {model} already exists. Skipping...")
            continue
        ciena.launch(
            model=model,
            input_folder=f"./data/datasets/work_ds/{test_case}/json",
            output_folder=f"./tests/{test_case}/{model}/",
        )

if __name__ == "__main__":
    main()