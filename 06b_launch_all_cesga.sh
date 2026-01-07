# Job for fastest-no-summary detect
# Job already exists at results/work/detect/fastest-no-summary, skipping...
# Job for fastest-summary detect
# Job already exists at results/work/detect/fastest-summary, skipping...
# Job for efficient-no-summary detect
# Job already exists at results/work/detect/efficient-no-summary, skipping...
# Job for efficient-summary detect
# Job already exists at results/work/detect/efficient-summary, skipping...
# Job for bestf1-no-summary detect

export RESULTS_DIR=results/work/detect/bestf1-no-summary/slurm
export CIENA_LLM_MODEL=qwen2.5:3b-instruct-q4_K_M
export SH_MODEL="bestf1-no-summary"
export SH_DATASET="work"
export SH_TASK="detect"

echo sbatch -t 05:00:00 -o $RESULTS_DIR/slurm.out -e $RESULTS_DIR/slurm.err -c 64 --gres=gpu:a100:$SLURM_GPUS $(pwd)/06_sbatch.sh

sh 06_sbatch.sh

# Job for bestf1-summary detect

export RESULTS_DIR=results/work/detect/bestf1-summary/slurm
export CIENA_LLM_MODEL=qwen2.5:3b-instruct-q4_K_M
export SH_MODEL="bestf1-summary"
export SH_DATASET="work"
export SH_TASK="detect"

echo sbatch -t 05:00:00 -o $RESULTS_DIR/slurm.out -e $RESULTS_DIR/slurm.err -c 64 --gres=gpu:a100:$SLURM_GPUS $(pwd)/06_sbatch.sh

sh 06_sbatch.sh

