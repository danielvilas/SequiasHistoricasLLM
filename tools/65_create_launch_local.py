
import os

base_dir="results"

dss = ["work", "full"]
tasks = ["detect", "classify"] #["detect","classify"]
models = ["qwen25.3b","qwen25.7b", "qwen3.8b", "deepseek.8b"]
modes = ["no-summary","summary","summary-expert"]

# Estimaciones de tiempo con los datos de paper de CienaLLM
time_short="01:00:00" # 300 n por 4s = 20min
time_long="05:00:00" # 300 n por 40s = 200min (3h20) 

params={
  "qwen25.3b-no-summary":{"llm":"qwen2.5:3b-instruct-q4_K_M", "time":time_short},
  "qwen25.3b-summary":{"llm":"qwen2.5:3b-instruct-q4_K_M", "time":time_short},
  "qwen25.3b-summary-expert":{"llm":"qwen2.5:3b-instruct-q4_K_M", "time":time_short},
  "qwen25.7b-no-summary":{"llm":"qwen2.5:7b-instruct-q4_K_M", "time":time_short},
  "qwen25.7b-summary":{"llm":"qwen2.5:72b-instruct-q4_K_M", "time":time_short},
  "qwen25.7b-summary-expert":{"llm":"qwen2.5:72b-instruct-q4_K_M", "time":time_short},
  "qwen25.72b.cot-no-summary":{"llm":"qwen2.5:3b-instruct-q4_K_M", "time":time_long},
  "qwen25.72b.cot-summary":{"llm":"qwen2.5:3b-instruct-q4_K_M", "time":time_long},
  "qwen25.72b.cot-summary-expert":{"llm":"qwen2.5:7b-instruct-q4_K_M", "time":time_long},

  "qwen3.8b-no-summary":{"llm":"qwen3:8b", "time":time_short},
  "qwen3.8b-summary":{"llm":"qwen3:8b", "time":time_short},
  "qwen3.8b-summary-expert":{"llm":"qwen3:8b", "time":time_short},
  "deepseek.8b-no-summary":{"llm":"deepseek.8b-r1:8b", "time":time_short},
  "deepseek.8b-summary":{"llm":"deepseek.8b-r1:8b", "time":time_short},
  "deepseek.8b-summary-expert":{"llm":"deepseek.8b-r1:8b", "time":time_short},
  "qwen3.32b.cot-no-summary":{"llm":"qwen3:30b", "time":time_long},
  "qwen3.32b.cot-summary":{"llm":"qwen3:30b", "time":time_long},
  "qwen3.32b.cot-summary-expert":{"llm":"qwen3:30b", "time":time_long},

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
                