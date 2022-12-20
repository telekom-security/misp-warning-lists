#!/bin/bash
# command to be run by cron: $ git pull origin; bash run.sh

# just development branch - should be removed in production
git checkout redesign

# update submodule repo
(
  cd misp-warninglists || exit
  git pull origin
)
./.venv_submodule/bin/python3 -m pip install -r misp-warninglists/requirements.txt
# requirements.txt currently contains "broken" version of pyOpenSSL (19.1.0) and therefore we upgrade it all the time
./.venv_submodule/bin/python3 -m pip install pyOpenSSL --upgrade


# generate updated warning lists
bash generate_lists.sh
.venv/bin/python3 merge_lists.py --warninglists misp
.venv/bin/python3 merge_lists.py --warninglists tsec


# save lists back to repo
git add lists/*
git commit -m"automatic warning-list update"
git push origin
