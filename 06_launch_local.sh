# Job for qwen25.3b-no-summary detect
# Job already exists at results/work/detect/qwen25.3b-no-summary, skipping...
# Job for qwen25.3b-summary detect
# Job already exists at results/work/detect/qwen25.3b-summary, skipping...
# Job for qwen25.3b-summary-expert detect
# Job already exists at results/work/detect/qwen25.3b-summary-expert, skipping...
# Job for qwen25.7b-no-summary detect
# Job already exists at results/work/detect/qwen25.7b-no-summary, skipping...
# Job for qwen25.7b-summary detect
# Job already exists at results/work/detect/qwen25.7b-summary, skipping...
# Job for qwen25.7b-summary-expert detect
# Job already exists at results/work/detect/qwen25.7b-summary-expert, skipping...
# Job for qwen3.8b-no-summary detect
# Job already exists at results/work/detect/qwen3.8b-no-summary, skipping...
# Job for qwen3.8b-summary detect
# Job already exists at results/work/detect/qwen3.8b-summary, skipping...
# Job for qwen3.8b-summary-expert detect
# Job already exists at results/work/detect/qwen3.8b-summary-expert, skipping...
# Job for deepseek.8b-no-summary detect
# Job already exists at results/work/detect/deepseek.8b-no-summary, skipping...
# Job for deepseek.8b-summary detect
# Job already exists at results/work/detect/deepseek.8b-summary, skipping...
# Job for deepseek.8b-summary-expert detect
# Job already exists at results/work/detect/deepseek.8b-summary-expert, skipping...
# Job for qwen25.3b-no-summary classify
# Job already exists at results/work/classify/qwen25.3b-no-summary, skipping...
# Job for qwen25.3b-summary classify
# Job already exists at results/work/classify/qwen25.3b-summary, skipping...
# Job for qwen25.3b-summary-expert classify

ollama pull qwen2.5:3b-instruct-q4_K_M
python 06_launch_ciena.py work qwen25.3b-summary-expert classify


# Job for qwen25.7b-no-summary classify
# Job already exists at results/work/classify/qwen25.7b-no-summary, skipping...
# Job for qwen25.7b-summary classify
# Job already exists at results/work/classify/qwen25.7b-summary, skipping...
# Job for qwen25.7b-summary-expert classify

ollama pull qwen2.5:72b-instruct-q4_K_M
python 06_launch_ciena.py work qwen25.7b-summary-expert classify


# Job for qwen3.8b-no-summary classify

ollama pull qwen3:8b
python 06_launch_ciena.py work qwen3.8b-no-summary classify


# Job for qwen3.8b-summary classify

ollama pull qwen3:8b
python 06_launch_ciena.py work qwen3.8b-summary classify


# Job for qwen3.8b-summary-expert classify

ollama pull qwen3:8b
python 06_launch_ciena.py work qwen3.8b-summary-expert classify


# Job for deepseek.8b-no-summary classify

ollama pull deepseek.8b-r1:8b
python 06_launch_ciena.py work deepseek.8b-no-summary classify


# Job for deepseek.8b-summary classify

ollama pull deepseek.8b-r1:8b
python 06_launch_ciena.py work deepseek.8b-summary classify


# Job for deepseek.8b-summary-expert classify

ollama pull deepseek.8b-r1:8b
python 06_launch_ciena.py work deepseek.8b-summary-expert classify


# Job for qwen25.3b-no-summary detect
# Job already exists at results/full/detect/qwen25.3b-no-summary, skipping...
# Job for qwen25.3b-summary detect
# Job already exists at results/full/detect/qwen25.3b-summary, skipping...
# Job for qwen25.3b-summary-expert detect

ollama pull qwen2.5:3b-instruct-q4_K_M
python 06_launch_ciena.py full qwen25.3b-summary-expert detect


# Job for qwen25.7b-no-summary detect
# Job already exists at results/full/detect/qwen25.7b-no-summary, skipping...
# Job for qwen25.7b-summary detect
# Job already exists at results/full/detect/qwen25.7b-summary, skipping...
# Job for qwen25.7b-summary-expert detect

ollama pull qwen2.5:72b-instruct-q4_K_M
python 06_launch_ciena.py full qwen25.7b-summary-expert detect


# Job for qwen3.8b-no-summary detect

ollama pull qwen3:8b
python 06_launch_ciena.py full qwen3.8b-no-summary detect


# Job for qwen3.8b-summary detect

ollama pull qwen3:8b
python 06_launch_ciena.py full qwen3.8b-summary detect


# Job for qwen3.8b-summary-expert detect

ollama pull qwen3:8b
python 06_launch_ciena.py full qwen3.8b-summary-expert detect


# Job for deepseek.8b-no-summary detect

ollama pull deepseek.8b-r1:8b
python 06_launch_ciena.py full deepseek.8b-no-summary detect


# Job for deepseek.8b-summary detect

ollama pull deepseek.8b-r1:8b
python 06_launch_ciena.py full deepseek.8b-summary detect


# Job for deepseek.8b-summary-expert detect

ollama pull deepseek.8b-r1:8b
python 06_launch_ciena.py full deepseek.8b-summary-expert detect


# Job for qwen25.3b-no-summary classify
# Job already exists at results/full/classify/qwen25.3b-no-summary, skipping...
# Job for qwen25.3b-summary classify
# Job already exists at results/full/classify/qwen25.3b-summary, skipping...
# Job for qwen25.3b-summary-expert classify

ollama pull qwen2.5:3b-instruct-q4_K_M
python 06_launch_ciena.py full qwen25.3b-summary-expert classify


# Job for qwen25.7b-no-summary classify
# Job already exists at results/full/classify/qwen25.7b-no-summary, skipping...
# Job for qwen25.7b-summary classify
# Job already exists at results/full/classify/qwen25.7b-summary, skipping...
# Job for qwen25.7b-summary-expert classify

ollama pull qwen2.5:72b-instruct-q4_K_M
python 06_launch_ciena.py full qwen25.7b-summary-expert classify


# Job for qwen3.8b-no-summary classify

ollama pull qwen3:8b
python 06_launch_ciena.py full qwen3.8b-no-summary classify


# Job for qwen3.8b-summary classify

ollama pull qwen3:8b
python 06_launch_ciena.py full qwen3.8b-summary classify


# Job for qwen3.8b-summary-expert classify

ollama pull qwen3:8b
python 06_launch_ciena.py full qwen3.8b-summary-expert classify


# Job for deepseek.8b-no-summary classify

ollama pull deepseek.8b-r1:8b
python 06_launch_ciena.py full deepseek.8b-no-summary classify


# Job for deepseek.8b-summary classify

ollama pull deepseek.8b-r1:8b
python 06_launch_ciena.py full deepseek.8b-summary classify


# Job for deepseek.8b-summary-expert classify

ollama pull deepseek.8b-r1:8b
python 06_launch_ciena.py full deepseek.8b-summary-expert classify


