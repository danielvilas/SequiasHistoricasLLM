
export SLURM_JOB_TIME="02:00:00"
export SLURM_CPUS=64
export SLURM_GPUS=2

export RESULTS_DIR=$HOME/SequiasHistoricasLLM/results/sbach_test
export CIENA_LLM_MODEL="qwen2.5:3b-instruct-q4_K_M"
export SH_MODEL="qwen25.3b-no-summary"
export SH_DATASET="work"
export SH_TASK="detect"


sbatch \
    -t $SLURM_JOB_TIME \
    -o $RESULTS_DIR/slurm.out \
    -e $RESULTS_DIR/slurm.err \
    -c $SLURM_CPUS \
    --gres=gpu:a100:$SLURM_GPUS \
    $(pwd)/05_sbach.sh