#! /usr/bin/env bash

set -x
set -e

pip install pip==20.3.1 setuptools==50.3.2
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
python get-poetry.py -y
source $HOME/.poetry/env
