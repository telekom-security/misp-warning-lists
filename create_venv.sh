#!/bin/bash

################# CONFIG #########################

submodule_python_version='3.10.8'
submodule_requirements_txt='./misp-warninglists_submodule/requirements.txt'

main_python_version='3.9.15'
main_requirements_txt='./requirements.txt'

###################################################

if ! (pyenv versions | grep $submodule_python_version) ; then
  pyenv install $submodule_python_version
fi
pyenv local $submodule_python_version
python -m venv .venv_submodule
.venv_submodule/bin/python -m pip install -r $submodule_requirements_txt


if ! pyenv versions | grep $main_python_version; then
  pyenv install $main_python_version
fi
pyenv local $main_python_version
python -m venv .venv
.venv/bin/python -m pip install -r $main_requirements_txt


########
# mv .venv_submodule/bin/python .venv_submodule/bin/python_original
# ln -s "$PWD"/python_wrapper.sh "$PWD"/.venv_submodule/bin/python



