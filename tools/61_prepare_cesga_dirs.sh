#!/bin/bash

mkdir -p $LUSTRE/.ollama
ln -sfn $LUSTRE/.ollama $HOME/.ollama

mkdir -p $STORE/.cache/pypoetry
mkdir -p $HOME/.cache
ln -sfn $STORE/.cache/pypoetry $HOME/.cache/pypoetry

curl -sSL https://install.python-poetry.org | python3 -
alias poetry="$HOME/.local/bin/poetry"

mkdir -p $STORE/datasets
ln -sfn $STORE/datasets $HOME/SequiasHistoricasLLM/data