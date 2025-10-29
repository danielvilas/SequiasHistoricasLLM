#Python update
python3 -m venv --upgrade-deps .venv
. .venv/bin/activate
pip install poetry
poetry install
pip install -e . 