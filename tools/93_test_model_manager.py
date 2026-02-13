from sequias_historicas.ModelManager import ModelManager

modelManager=ModelManager.load_yaml_config()

tasks = ["detect", "classify"] #["detect","classify"]
models = ["qwen25.3b","qwen25.7b","qwen25.72b.cot", "qwen3.8b", "qwen3.32b.cot","deepseek.8b"]
modes = ["no-summary","summary","summary-expert"]

def main():

    print ("Available models:")
    print(modelManager.get_available_models())

    for task in tasks:
        for model in models:
            for mode in modes:
                config = f"{task}-{model}-{mode}"
                t_model=modelManager.get_model_config(config)
                #print(t_model.config)
                #print(modelManager.get_model_config(config).config)
    pass

if __name__ == "__main__":
    main()