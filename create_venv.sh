#!/bin/bash

### CONFIG:
submodule_requirements_txt='./misp-warninglists/requirements.txt'
main_requirements_txt='./requirements.txt'

##############################
python3 -m venv .venv_submodule
.venv_submodule/bin/python3 -m pip install -r $submodule_requirements_txt
.venv_submodule/bin/python3 -m pip install --upgrade pip
.venv_submodule/bin/python3 -m pip install pyOpenSSL --upgrade

python3 -m venv .venv
.venv/bin/python3 -m pip install -r $main_requirements_txt
.venv/bin/python3 -m pip install --upgrade pip
