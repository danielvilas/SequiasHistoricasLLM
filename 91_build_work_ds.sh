#!/bin/bash

rm -r data/datasets/work_ds
rm -r data/datasets/json_test

mkdir -p data/datasets/work_ds
python 91_get_Json_sample.py 10
mv data/datasets/json_test data/datasets/work_ds/test_10

python 91_get_Json_sample.py
mv data/datasets/json_test data/datasets/work_ds/test_full