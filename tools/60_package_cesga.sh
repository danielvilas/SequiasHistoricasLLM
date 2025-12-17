#!/bin/bash

# Script to package CESGA-files
# Requieres:
# - tar
# - gzip
# - scp
# - CESGA Account configured on ~/.ssh/config to conect without password


echo "Packaging CESGA files..."

tar -cvzf cesga_files.tar.gz src *.py tools *.sh poetry.lock pyproject.toml data/datasets/work_ds data/models*
scp cesga_files.tar.gz ft3.cesga.es:./SequiasHistoricasLLM
rm cesga_files.tar.gz
echo "Package cesga_files.tar.gz uploaded to CESGA"