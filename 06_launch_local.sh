# Job for fastest-no-summary detect
# Job already exists at results/work/detect/fastest-no-summary, skipping...
# Job for fastest-summary detect
# Job already exists at results/work/detect/fastest-summary, skipping...
# Job for fastest-summary-expert detect
# Job already exists at results/work/detect/fastest-summary-expert, skipping...
# Job for efficient-no-summary detect
# Job already exists at results/work/detect/efficient-no-summary, skipping...
# Job for efficient-summary detect
# Job already exists at results/work/detect/efficient-summary, skipping...
# Job for efficient-summary-expert detect
# Job already exists at results/work/detect/efficient-summary-expert, skipping...
# Job for efficient3-no-summary detect
# Job already exists at results/work/detect/efficient3-no-summary, skipping...
# Job for efficient3-summary detect
# Job already exists at results/work/detect/efficient3-summary, skipping...
# Job for efficient3-summary-expert detect
# Job already exists at results/work/detect/efficient3-summary-expert, skipping...
# Job for deepseek-no-summary detect
# Job already exists at results/work/detect/deepseek-no-summary, skipping...
# Job for deepseek-summary detect
# Job already exists at results/work/detect/deepseek-summary, skipping...
# Job for deepseek-summary-expert detect
# Job already exists at results/work/detect/deepseek-summary-expert, skipping...
# Job for fastest-no-summary classify
# Job already exists at results/work/classify/fastest-no-summary, skipping...
# Job for fastest-summary classify
# Job already exists at results/work/classify/fastest-summary, skipping...
# Job for fastest-summary-expert classify

ollama pull qwen2.5:3b-instruct-q4_K_M
python 06_launch_ciena.py work fastest-summary-expert classify


# Job for efficient-no-summary classify
# Job already exists at results/work/classify/efficient-no-summary, skipping...
# Job for efficient-summary classify
# Job already exists at results/work/classify/efficient-summary, skipping...
# Job for efficient-summary-expert classify

ollama pull qwen2.5:72b-instruct-q4_K_M
python 06_launch_ciena.py work efficient-summary-expert classify


# Job for efficient3-no-summary classify

ollama pull qwen3:8b
python 06_launch_ciena.py work efficient3-no-summary classify


# Job for efficient3-summary classify

ollama pull qwen3:8b
python 06_launch_ciena.py work efficient3-summary classify


# Job for efficient3-summary-expert classify

ollama pull qwen3:8b
python 06_launch_ciena.py work efficient3-summary-expert classify


# Job for deepseek-no-summary classify

ollama pull deepseek-r1:8b
python 06_launch_ciena.py work deepseek-no-summary classify


# Job for deepseek-summary classify

ollama pull deepseek-r1:8b
python 06_launch_ciena.py work deepseek-summary classify


# Job for deepseek-summary-expert classify

ollama pull deepseek-r1:8b
python 06_launch_ciena.py work deepseek-summary-expert classify


# Job for fastest-no-summary detect
# Job already exists at results/full/detect/fastest-no-summary, skipping...
# Job for fastest-summary detect
# Job already exists at results/full/detect/fastest-summary, skipping...
# Job for fastest-summary-expert detect

ollama pull qwen2.5:3b-instruct-q4_K_M
python 06_launch_ciena.py full fastest-summary-expert detect


# Job for efficient-no-summary detect
# Job already exists at results/full/detect/efficient-no-summary, skipping...
# Job for efficient-summary detect
# Job already exists at results/full/detect/efficient-summary, skipping...
# Job for efficient-summary-expert detect

ollama pull qwen2.5:72b-instruct-q4_K_M
python 06_launch_ciena.py full efficient-summary-expert detect


# Job for efficient3-no-summary detect

ollama pull qwen3:8b
python 06_launch_ciena.py full efficient3-no-summary detect


# Job for efficient3-summary detect

ollama pull qwen3:8b
python 06_launch_ciena.py full efficient3-summary detect


# Job for efficient3-summary-expert detect

ollama pull qwen3:8b
python 06_launch_ciena.py full efficient3-summary-expert detect


# Job for deepseek-no-summary detect

ollama pull deepseek-r1:8b
python 06_launch_ciena.py full deepseek-no-summary detect


# Job for deepseek-summary detect

ollama pull deepseek-r1:8b
python 06_launch_ciena.py full deepseek-summary detect


# Job for deepseek-summary-expert detect

ollama pull deepseek-r1:8b
python 06_launch_ciena.py full deepseek-summary-expert detect


# Job for fastest-no-summary classify
# Job already exists at results/full/classify/fastest-no-summary, skipping...
# Job for fastest-summary classify
# Job already exists at results/full/classify/fastest-summary, skipping...
# Job for fastest-summary-expert classify

ollama pull qwen2.5:3b-instruct-q4_K_M
python 06_launch_ciena.py full fastest-summary-expert classify


# Job for efficient-no-summary classify
# Job already exists at results/full/classify/efficient-no-summary, skipping...
# Job for efficient-summary classify
# Job already exists at results/full/classify/efficient-summary, skipping...
# Job for efficient-summary-expert classify

ollama pull qwen2.5:72b-instruct-q4_K_M
python 06_launch_ciena.py full efficient-summary-expert classify


# Job for efficient3-no-summary classify

ollama pull qwen3:8b
python 06_launch_ciena.py full efficient3-no-summary classify


# Job for efficient3-summary classify

ollama pull qwen3:8b
python 06_launch_ciena.py full efficient3-summary classify


# Job for efficient3-summary-expert classify

ollama pull qwen3:8b
python 06_launch_ciena.py full efficient3-summary-expert classify


# Job for deepseek-no-summary classify

ollama pull deepseek-r1:8b
python 06_launch_ciena.py full deepseek-no-summary classify


# Job for deepseek-summary classify

ollama pull deepseek-r1:8b
python 06_launch_ciena.py full deepseek-summary classify


# Job for deepseek-summary-expert classify

ollama pull deepseek-r1:8b
python 06_launch_ciena.py full deepseek-summary-expert classify


