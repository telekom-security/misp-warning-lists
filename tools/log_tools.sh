# runs and logs usage and its return code

log_command(){
  timestamp_start=$(date +"%s")

  $@ # this runs whatever the function gets as a parameter
  exit_code=$?

  exec_time=$(($(date +"%s")-timestamp_start))
  logger="generator"
  command=$*
  if [ $exit_code -eq 0 ]; then
    log_level="INFO"
  else
    log_level="ERROR"
  fi

  msg="command {'command': '${command}', 'exit_code': ${exit_code}, 'pwd': '${PWD}', 'timestamp_start': ${timestamp_start}, 'exec_time': ${exec_time}}"
  log_msg "$logger" "$log_level" "$msg"
}

log_msg(){
  log_time=$(date "+%Y-%m-%d %H:%M:%S,%3N")
  echo "${log_time} - $1 - $2 - $3" >> $WARNINGLISTS_LOG_FILE
}
