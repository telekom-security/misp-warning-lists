#!/bin/bash
# command to be run by cron: "git pull origin; bash run.sh"

git checkout redesign # just development branch - should be removed in production (similarly "git push" at the end of this script!)

# update submodule sourcecode
(
  cd misp-warninglists || exit
  if [ -f .git ]; then
    git pull origin
  else
    git submodule update --init --recursive
  fi
)


# update all source codes and venvs
bash ./create_or_update_env.sh

export WARNINGLISTS_RUN_ID=$(date "%Y%m%d%H%M%S%3N")
export WARNINGLISTS_LOG_FILE="/var/log/misp-warning-lists/misp-warning-lists.log"

# generate updated warning lists
bash generate_lists.sh
.venv/bin/python3 merge_lists.py --warninglists misp
.venv/bin/python3 merge_lists.py --warninglists tsec


# save lists back to repo
git add lists/*
git commit -m"automatic warning-list update"
git push origin redesign
