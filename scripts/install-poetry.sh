#! /usr/bin/env bash

set -x
set -e

curl -fsS -o get-poetry.py https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py
python get-poetry.py -y
echo "$HOME/.poetry/bin" >> $GITHUB_PATH
