from sequias_historicas.ModelManager import ModelManager

modelManager=ModelManager.load_yaml_config()

def main():
    model=modelManager.get_model_config("fastest-no-summary")
    print(model.config)
    print(modelManager.get_model_config("fastest-summary").config)
    pass

if __name__ == "__main__":
    main()