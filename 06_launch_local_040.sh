#!/bin/sh

python 06_launch_ciena.py work fastest-no-summary detect
python 06_launch_ciena.py work fastest-summary detect
python 06_launch_ciena.py work efficient-no-summary detect
python 06_launch_ciena.py work efficient-summary detect
python 06_launch_ciena.py work bestf1-no-summary detect
python 06_launch_ciena.py work bestf1-summary detect


python 06_launch_ciena.py work efficient3-no-summary detect
python 06_launch_ciena.py work efficient3-summary detect
python 06_launch_ciena.py work deepseek-no-summary detect
#python 06_launch_ciena.py work deepseek-summary detect
#python 06_launch_ciena.py work bestf13-no-summary detect
#python 06_launch_ciena.py work bestf13-summary detect

python 06_launch_ciena.py full fastest-no-summary detect
python 06_launch_ciena.py full fastest-summary detect
python 06_launch_ciena.py full efficient-no-summary detect
python 06_launch_ciena.py full efficient-summary detect
# python 06_launch_ciena.py work bestf1-no-summary detect
# python 06_launch_ciena.py work bestf1-summary detect



