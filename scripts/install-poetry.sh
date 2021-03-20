#! /usr/bin/env bash

set -x
set -e

pip install pip==20.3.1 setuptools==50.3.2
curl -fsS -o get-poetry.py https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py
python get-poetry.py -y
source $HOME/.poetry/env
