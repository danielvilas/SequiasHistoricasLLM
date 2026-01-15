
import os

base_dir="results"

dss = ["work", "full"]
tasks = ["detect", "classify"] #["detect","classify"]
models = ["fastest","efficient", "efficient3", "deepseek"]
modes = ["no-summary","summary","summary-expert"]

# Estimaciones de tiempo con los datos de paper de CienaLLM
time_short="01:00:00" # 300 n por 4s = 20min
time_long="05:00:00" # 300 n por 40s = 200min (3h20) 

params={
  "fastest-no-summary":{"llm":"qwen2.5:3b-instruct-q4_K_M", "time":time_short},
  "fastest-summary":{"llm":"qwen2.5:3b-instruct-q4_K_M", "time":time_short},
  "fastest-summary-expert":{"llm":"qwen2.5:3b-instruct-q4_K_M", "time":time_short},
  "efficient-no-summary":{"llm":"qwen2.5:7b-instruct-q4_K_M", "time":time_short},
  "efficient-summary":{"llm":"qwen2.5:72b-instruct-q4_K_M", "time":time_short},
  "efficient-summary-expert":{"llm":"qwen2.5:72b-instruct-q4_K_M", "time":time_short},
  "bestf1-no-summary":{"llm":"qwen2.5:3b-instruct-q4_K_M", "time":time_long},
  "bestf1-summary":{"llm":"qwen2.5:3b-instruct-q4_K_M", "time":time_long},
  "bestf1-summary-expert":{"llm":"qwen2.5:7b-instruct-q4_K_M", "time":time_long},

  "efficient3-no-summary":{"llm":"qwen3:8b", "time":time_short},
  "efficient3-summary":{"llm":"qwen3:8b", "time":time_short},
  "efficient3-summary-expert":{"llm":"qwen3:8b", "time":time_short},
  "deepseek-no-summary":{"llm":"deepseek-r1:8b", "time":time_short},
  "deepseek-summary":{"llm":"deepseek-r1:8b", "time":time_short},
  "deepseek-summary-expert":{"llm":"deepseek-r1:8b", "time":time_short},
  "bestf13-no-summary":{"llm":"qwen3:30b", "time":time_long},
  "bestf13-summary":{"llm":"qwen3:30b", "time":time_long},
  "bestf13-summary-expert":{"llm":"qwen3:30b", "time":time_long},

}

template = '''
ollama pull {llm}
python 06_launch_ciena.py {ds} {config} {task}

'''
for ds in dss:
    for task in tasks:
        for model in models:
            for mode in modes:
                config = f"{model}-{mode}"
                job_path = f"{base_dir}/{ds}/{task}/{config}"
                print (f"# Job for {config} {task}")
                if not os.path.exists(job_path):
                    os.makedirs(job_path,exist_ok=True)
                if os.path.exists(f"{job_path}/summary.csv"):
                    print (f"# Job already exists at {job_path}, skipping...")
                    continue
                print (template.format(job_path=job_path,
                                    params=params,
                                    config=config,
                                    ds=ds,task=task,
                                    llm=params[config]["llm"],
                                    cpus=64,
                                    time=params[config]["time"],
                                    gpu="gpu:a100:2"
                                    ))
                