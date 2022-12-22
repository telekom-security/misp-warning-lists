# logging to the file in variable $WARNINGLISTS_LOG_FILE and if variable $WARNINGLISTS_RUN_ID exists it adds it to the log

log_command(){
  # runs whatever the function gets as a parameter and logs its return code
  timestamp_start=$(date +"%s")

  # this runs whatever the function gets as a parameter and saves the stderr
  { stderr=$("$@" 2>&1 1>&$tmp_fd); } {tmp_fd}>&1

  exit_code=$?

  exec_time=$(($(date +"%s")-timestamp_start))
  logger="shell"
  command=$*
  if [ $exit_code -eq 0 ]; then
    log_level="INFO"
  else
    log_level="ERROR"
  fi

  msg="command {'command': '${command}', 'exit_code': ${exit_code}, 'pwd': '${PWD}', 'timestamp_start': ${timestamp_start}, 'exec_time': ${exec_time}, 'stderr': '$(echo $stderr)'}"
  log_msg "$logger" "$log_level" "$msg"
}

log_msg(){
  # format: $ log_msg "logger_name" "log_level" "message"

  log_time=$(date "+%Y-%m-%d %H:%M:%S,%3N")

  if [ -z "$WARNINGLISTS_RUN_ID" ]; then
    logger=$1;
  else
    logger="${1}[run_id:${WARNINGLISTS_RUN_ID}]"
  fi

  log_line="${log_time} - ${logger} - $2 - $3"
  if [ -z "$WARNINGLISTS_LOG_FILE" ]; then
    echo "$log_line"
  else
    echo "$log_line" >> "$WARNINGLISTS_LOG_FILE"
  fi
}
