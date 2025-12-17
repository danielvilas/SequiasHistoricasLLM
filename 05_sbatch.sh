#!/bin/bash
#----------------------------------------------------
# CienaLLM (test)
#----------------------------------------------------
#SBATCH --mem-per-cpu=3G             # Memory per core demandes
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=dvilas@csic.es

alias poetry="$HOME/.local/bin/poetry"

cd $HOME/SequiasHistoricasLLM/
mkdir -p $RESULTS_DIR
echo $SLURM_JOBID >$RESULTS_DIR/slurm.id


# Load Ollama and Python modules
module load cesga/2022 ollama/0.6.4 python/3.10.8

# Maximum number of retries (for port and server check)
MAX_RETRIES=5

ollama_server_start_t=$(date +%s)

# Set the Ollama port
if [ -z "$SLURM_JOBID" ]; then
    export OLLAMA_PORT=11434
else
    export OLLAMA_PORT=$(expr 10000 + $(echo -n $SLURM_JOBID | tail -c 4))
fi

# Check if the port is already in use and increment if necessary
RETRY_COUNT=0
while netstat -tuln | grep -q ":$OLLAMA_PORT"; do
    echo "Port $OLLAMA_PORT is already in use. Incrementing..."
    RETRY_COUNT=$(expr $RETRY_COUNT + 1)
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "Error: Could not find an available port after $MAX_RETRIES retries."
        exit 1
    fi
    export OLLAMA_PORT=$(expr $OLLAMA_PORT + 1)
done

export OLLAMA_HOST="127.0.0.1:$OLLAMA_PORT"
export OLLAMA_TMPDIR=$TMPDIR

# Start the Ollama server
ollama serve >$RESULTS_DIR/ollama_server.log 2>&1 &

RETRY_COUNT=0
while ! curl -s $OLLAMA_HOST | grep -q "Ollama is running"; do
    echo "Ollama server is not running. Retrying..."
    RETRY_COUNT=$(expr $RETRY_COUNT + 1)
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "Error: Ollama server is not running after $MAX_RETRIES retries."
        exit 1
    fi
    sleep 1
done

ollama_server_end_t=$(date +%s)

model_pull_start_t=$(date +%s)
# Pull the model if it does not exist
ollama pull $CIENA_LLM_MODEL
model_pull_end_t=$(date +%s)

warmup_start_t=$(date +%s)
# Warm-up the model
ollama run --keepalive 10m $CIENA_LLM_MODEL ""
warmup_end_t=$(date +%s)

cat <<EOF
----------------------------------------
Job Configuration:

SLURM_JOBID: $SLURM_JOBID

OLLAMA_PORT: $OLLAMA_PORT
OLLAMA_HOST: $OLLAMA_HOST
OLLAMA_TMPDIR: $OLLAMA_TMPDIR

RESULTS_DIR: $RESULTS_DIR

SH_MODEL: $SH_MODEL
SH_DATASET: $SH_DATASET
SH_TASK: $SH_TASK

Execution Times:

Ollama server setup: $(expr $ollama_server_end_t - $ollama_server_start_t) s.
Model pull: $(expr $model_pull_end_t - $model_pull_start_t) s.
Model warm-up: $(expr $warmup_end_t - $warmup_start_t) s.
----------------------------------------
EOF

# Run the test
experiment_start_t=$(date +%s)
echo poetry run python 05_launch_ciena.py $SH_DATASET $SH_MODEL $SH_TASK

experiment_end_t=$(date +%s)
echo "Experiment Execution Time (SLURM): $(expr $experiment_end_t - $experiment_start_t) s."