from sequias_historicas.CienaLauncher import CienaLauncher

ciena = CienaLauncher()

def main():
    print("This is a placeholder for the Ciena test module.")
    ciena.launch(
        model="gemma3:4b",
        input_folder="./data/datasets/json_test/json",
        output_folder="./tests/json_test"
    )
if __name__ == "__main__":
    main()