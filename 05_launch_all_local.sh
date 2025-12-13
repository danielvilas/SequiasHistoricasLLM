#!/bin/sh

python 05_launch_ciena.py work fastest-no-summary detect
python 05_launch_ciena.py work fastest-summary detect
python 05_launch_ciena.py work efficient-no-summary detect
python 05_launch_ciena.py work efficient-no-summary detect
python 05_launch_ciena.py work efficient-summary detect
python 05_launch_ciena.py work bestf1-no-summary detect
python 05_launch_ciena.py work bestf1-summary detect