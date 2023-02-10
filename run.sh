#!/bin/bash
# command to be run by cron: "git pull origin; bash run.sh"
export WARNINGLISTS_RUN_ID=$(date "+%Y%m%d%H%M%S%3N")
export WARNINGLISTS_LOG_FILE="/var/log/misp-warning-lists.log"
printf "\nrun_id:$WARNINGLISTS_RUN_ID\n\n"


source ./tools/log_tools.sh # load function log_command
log_msg "run.sh" "INFO" "start"

# update submodule sourcecode
(
  cd misp-warninglists || exit
  if [ -f .git ]; then
    git reset --hard HEAD
    git pull origin main
  else
    git submodule update --init --recursive
  fi
)


# update all source codes and venvs
log_command bash ./create_or_update_env.sh

# generate updated warning lists
bash generate_lists.sh
.venv/bin/python3 merge_lists.py --warninglists misp
.venv/bin/python3 merge_lists.py --warninglists tsec

# save lists back to repo
log_command git add misp-warninglists lists/*
log_command git commit -m "automatic warning-list update"
log_command git push origin master

log_msg "run.sh" "INFO" "finish"

