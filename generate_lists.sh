#!/bin/bash
# generate all warning lists in misp-warninglists_submodule and tsec-warninglists

# export WARNINGLISTS_RUN_ID=$(date "%Y%m%d%H%M%S%3N")
# export WARNINGLISTS_LOG_FILE="./misp-warning-lists.log"

source ./tools/log_tools.sh # load function log_command

log_msg "generator" "INFO" "start"
############################################################
# GENERATE MISP-WARNINGLISTS/LISTS/
############################################################

# there are two options for logging scripts
# - Either replacing python in .venv_submodule/bin by python_wrapper (which logs usage and error codes)
#   - we need it only if we run some shell scripts (misp-warninglists/generate_all.sh) which calls some python scripts internally.
# - Or if we run the python scripts directly from here then we can use log_command approach (as in tsec-warninglists/lists generation below) and then do not need to wrap the python

source tools/wrapper_tools.sh # load set_python_wrapper and unset_python_wrapper functions
export -f log_command log_msg # the python_wrapper needs log_command function
set_python_wrapper ./.venv_submodule/bin ./tools/python_wrapper.sh

source ./.venv_submodule/bin/activate
start_time=$(date "+%Y-%m-%d %H:%M:%S")
  (
  cd ./misp-warninglists || exit
  # here you can add the scripts for lists.json generation
  log_command bash ./generate_all.sh
  )
deactivate

unset_python_wrapper ./.venv_submodule/bin

# logging of all the lists modified during the misp-warninglist generation
modified_lists=$(find misp-warninglists/lists/ -name "list.json" -newermt "$start_time" | paste -sd ";";)
msg="warninglists {'name':'misp-warninglists', 'modified_lists': '${modified_lists}'}"
log_msg "generator" "INFO" "$msg"


############################################################
# GENERATE TSEC-WARNINGLISTS/LISTS/
############################################################

# generate all lists in tsec-warninglists
source ./.venv/bin/activate
start_time=$(date "+%Y-%m-%d %H:%M:%S")
  (
  cd ./tsec-warninglists || exit
  # here you can add the scripts for lists.json:
  log_command python3 generate-dns-root-servers.py
  )
deactivate

# logging of all lists which have been modified during the tsec-warninglist generation
modified_lists=$(find tsec-warninglists/lists/ -name "list.json" -newermt "$start_time" | paste -sd ";";)
msg="warninglists {'name':'tsec-warninglists', 'modified_lists': '${modified_lists}'}"
log_msg "generator" "INFO" "$msg"


