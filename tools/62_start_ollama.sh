module load cesga/2022 ollama/0.6.4 python/3.10.8
export OLLAMA_HOST="127.0.0.1:$((11434 + $SLURM_JOB_ID % 1000))"
export OLLAMA_TMPDIR=$TMPDIR

ollama serve &