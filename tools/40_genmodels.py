import yaml
from copy import deepcopy

base_models = ["fastest","efficient","bestf1"]
summary={"no-summary":None,
         "summary":{"steps":{"summarization":{"enable": True}}},
         "summary-expert":{"steps":{"summarization":{"enable": True,"prompt":{"language":"en-expert"}}}}
         }
actions = ["detect","classify"]

extra_models = {"efficient3":{"llm":"qwen3:8b","base":"efficient"},
                "bestf13":{"llm":"qwen3:30b","base":"bestf1"},
                "deepseek":{"llm":"deepseek-r1:8b","base":"efficient"}
                }

def build_model(action:str, base_model:str, summ:str):
        
    base = f"{action}-{base_model}"
    model_name = f"{base}-{summ}"
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
        for base_model in base_models+list(extra_models.keys()):
            for summ in summary:
                cfg = build_model(action, base_model, summ)
                models["models"].append(cfg)

    with open("genmodels.yaml", "w") as f:
        yaml.safe_dump(models, f)
    pass


if __name__ == "__main__":
    main()