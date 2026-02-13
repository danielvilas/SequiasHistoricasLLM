import yaml
from copy import deepcopy

base_models = {"fastest":"qwen25.3b","efficient":"qwen25.7b","bestf1":"qwen25.72b.cot"}
summary={"no-summary":None,
         "summary":{"steps":{"summarization":{"enable": True}}},
         "summary-expert":{"steps":{"summarization":{"enable": True,"prompt":{"language":"en-expert"}}}}
         }
actions = ["detect","classify"]

extra_models = {"qwen3.8b":{"llm":"qwen3:8b","base":"efficient"},
                "qwen3.32b.cot":{"llm":"qwen3:32b","base":"bestf1"},
                "deepseek.8b":{"llm":"deepseek-r1:8b","base":"efficient"}
                }

def build_model(action:str, base_model:str, summ:str):
        
    base = f"{action}-{base_model}"

    if base_model in base_models:
        model_name = f"{action}-{base_models[base_model]}-{summ}"
    else:
        model_name = f"{action}-{base_model}-{summ}"
    cfg = {
        "name": model_name,
        "base": base,
    }
    if summary[summ]:
        cfg.update({"overrides": deepcopy(summary[summ])})
    if base_model in extra_models:
        if "overrides" not in cfg:
            cfg["overrides"] = {}
        cfg["base"] = action+"-"+extra_models[base_model]["base"]        
        cfg["overrides"]["llm"] = {"name": extra_models[base_model]["llm"],
                                    "thinking":True}

    return cfg



def main():
    models={"models":[]}
    for action in actions:
        for base_model in list(base_models.keys())+list(extra_models.keys()):
            for summ in summary:
                cfg = build_model(action, base_model, summ)
                models["models"].append(cfg)

    with open("genmodels.yaml", "w") as f:
        yaml.safe_dump(models, f)
    pass


if __name__ == "__main__":
    main()