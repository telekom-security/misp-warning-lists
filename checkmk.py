#!/usr/bin/python3

import os
import re
import ast
import sys
import datetime as dt


def print_output(status_code, service_name, metrics, msg, exit_after=False):
    """
    :param status_code: 0 .. OK, 1 .. WARNING, 2 .. ERROR, 3 .. UNKNOWN, P .. CheckMK automatically decides based on warn and error ranges
    :param metrics: either str (e.g. "-") or dict or list of dicts
    """

    if isinstance(metrics, str):
        final_metrics = metrics
    elif isinstance(metrics, (dict, tuple, list)):
        final_metrics = format_metrics(metrics)
    else:
        raise TypeError(f"Metrics type {type(metrics)} is not supported.")

    output = '{status_code} {service_name} {metrics} {msg}'
    print(output.format(status_code=status_code,
                        service_name=service_name,
                        metrics=final_metrics,
                        msg=msg))
    if exit_after:
        sys.exit(0)


def format_metrics(metrics_dict):
    """ formats metric and multi-metrics with all the allowed parameters: https://docs.checkmk.com/latest/en/localchecks.html

    :param metrics_dict: one metric_dict or list of them
     - one metric_dict: {valuename="", value="", warn_lower="", warn_upper="", error_lower="", error_upper="", min="", max=""}
     - all the values (except 'valuename' and 'value') can be either missing or set to an empty string
    :return: string 'valuename=value;warn_lower:warn_upper;crit_lower:crit_upper;min;max'
    """
    if isinstance(metrics_dict, dict):
        metrics_dict = [metrics_dict]

    metrics_str = []
    for m in metrics_dict:
        warn = f"{m.get('warn_lower', '')}" + (":" if m.get("warn_lower", "") != "" else "") + f"{m.get('warn_upper', '')}"
        error = f"{m.get('error_lower', '')}" + (":" if m.get("error_lower", "") != "" else "") + f"{m.get('error_upper', '')}"
        m_str = '{valuename}={value};{warn};{error};{min};{max}'.format(
            valuename=m["valuename"],
            value=m["value"],
            warn=warn,
            error=error,
            min=m.get("min", ""),
            max=m.get("max", "")
        )
        metrics_str.append(m_str.strip(";"))
    return "|".join(metrics_str)


# ----------------------- CONFIGURATION --------------------------------------
service_name = 'MISP-warninglists'

TIME_WINDOW = 100  # reading logs N minutes back

log_dir = "."
log_base_file_name = "my.log"  # script checks also not-compressed rotated logs with suffix ".1", ".2", ...


# -------------------------------- CHECK ---------------------------------------
class LogFileReader:
    n_warnings = 0
    n_errors = 0
    n_command_errors = 0
    n_new_command_errors = 0

    warning_msg = ""
    error_msg = ""

    def __init__(self):
        # log format: "2020-12-24 18:00:00,001 - logger - INFO - msg {'a':0, 'b': '...'}"
        self._log_pattern = re.compile(r"^(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (?P<app>.*?) - (?P<level>\w*?) - (?P<msg>.*)$")
        self._msg_pattern = re.compile(r"(?P<pref>.*?)(?P<params>\{.*\})$")

    def _parse_log_line(self, log_line):
        log_time, log_app, log_level, msg = None, None, None, None
        msg_pref, msg_params = None, None

        log_line_parsed = self._log_pattern.match(log_line)
        if log_line_parsed is not None:
            log_time, log_app, log_level, msg = log_line_parsed.group("time", "app", "level", "msg")
            msg_parsed = self._msg_pattern.match(msg)
            if msg_parsed is not None:
                msg, msg_params = msg_parsed.group("pref"), msg_parsed.group("params")
            msg_params = ast.literal_eval(msg_params) if msg_parsed else None

        return (log_time, log_app, log_level, msg.strip() if msg is not None else None, msg_params)

    def iter_log(self, log_file_name: str, time_from: dt.datetime):
        """iter only loglines in given format (self._log_pattern), the other lines are skipped"""
        with open(log_file_name, "r", encoding="utf-8") as log_file:
            time_from_str = time_from.strftime("%Y-%m-%d %H:%M:%S")
            for log_line in log_file:
                if log_line < time_from_str:  # timestamp on the log_line lower then threshold
                    continue
                log_time, log_app, log_level, log_msg, log_msg_params = self._parse_log_line(log_line)
                if log_time is not None:
                    yield log_time, log_app, log_level, log_msg, log_msg_params

    def read(self, log_file_name: str, time_from: dt.datetime):
        """ processing lines of log file. Skips log_line with lower time stamp then 'time_from' """
        commands_state = {}  # command: (time_start, exit_code)
        generator_starts = []  # list of start_times of generator scripts

        for log_time, log_app, log_level, log_msg, log_msg_params in self.iter_log(log_file_name, time_from=time_from):

            if log_app == "generator" and log_msg == "command":
                cmd = f"{log_msg_params['pwd']}$ {log_msg_params['command']}"
                states = commands_state.get(cmd, [])
                states.append((log_time, log_msg_params["exit_code"]))
                commands_state[cmd] = states

            if log_app == "generator" and log_msg == "start":
                generator_starts.append(log_time)

            if log_level == "WARNING":
                self.n_warnings += 1
                self.warning_msg += f"{log_msg} {log_msg_params}"

            if log_level in ["ERROR", "CRITICAL"]:
                if log_app == "pymisp" and "A similar attribute already exists for this event" in log_msg_params:
                    continue
                self.n_errors += 1
                self.error_msg += f"{log_msg} {log_msg_params}"

        # compares exit_codes of the last two runs for each command
        if len(generator_starts) >= 2:
            generator_starts.sort(reverse=True)
            current_generator_start, previous_generator_start = generator_starts[0], generator_starts[1]
            for command, time_state in commands_state.items():
                previous_run = sorted(filter(lambda t: t[0] >= current_generator_start, time_state))
                current_run = sorted(filter(lambda t: current_generator_start > t[0] >= previous_generator_start, time_state))
                if not (previous_run and current_run):  # either current run or previous run does not contain given command execution
                    continue
                if previous_run[0][1] == 0 and current_run[0][1] != 0:
                    self.n_new_command_errors += 1


# ------------- Reading logs ------------
reader = LogFileReader()

time_from = dt.datetime.now()-dt.timedelta(minutes=TIME_WINDOW)

# reads all the rotated log files in log_dir which has been modified within the given time_window
log_file_name_template = re.compile(f"^{re.escape(log_base_file_name)}(.[0-9]+)?$")  # rotated log files (e.g. my.log, my.log.1, my.log.2, ...)
for file_name in [f for f in os.listdir(log_dir) if re.match(log_file_name_template, f)]:
    log_file_name = os.path.join(log_dir, file_name)
    if os.lstat(log_file_name).st_mtime >= time_from.timestamp():
        reader.read(log_file_name, time_from=time_from)

metrics = [dict(valuename="number_of_errors",
                value=reader.n_errors),

           dict(valuename="number_of_warnings",
                value=reader.n_warnings),

           dict(valuename="number_of_new_errors",
                value=reader.n_new_command_errors,
                error_upper=1)
           ]

status_code = "P"
msg = "ok"

print_output(status_code, service_name, metrics, msg)