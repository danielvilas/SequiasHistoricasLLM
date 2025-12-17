#!/bin/bash

# Script to package CESGA-files
# Requieres:
# - tar
# - gzip
# - scp
# - CESGA Account configured on ~/.ssh/config to conect without password


echo "Packaging CESGA files..."

tar -cvzf cesga_files.tar.gz src data/datasets/work_ds results
scp cesga_files.tar.gz ft3.cesga.es:./SequiasHistoricasLLM
rm cesga_files.tar.gz
echo "Package cesga_files.tar.gz uploaded to CESGA"