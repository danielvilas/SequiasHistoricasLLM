from sequias_historicas.ModelManager import ModelManager
def main():
    manager = ModelManager.load_yaml_config()
    print("Installation test passed.")

if __name__ == "__main__":
    main()