#!/usr/bin/python3
# (this script is probably overcomplicated and should be simplified once we get more experiences/requirements for merging lists)

import os
import sys
import json
import shutil
import logging
import traceback
import argparse
import configparser
from pathlib import Path

import tools.validate_values as validator

logger_name = "merger"
logger_name += f"[run_id:{os.environ['WARNINGLISTS_RUN_ID']}]" if "WARNINGLISTS_RUN_ID" in os.environ else ""
logger = logging.getLogger(logger_name)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.environ.get('WARNINGLISTS_LOG_FILE', "") # if $WARNINGLISTS_LOG_FILE does not exists then it logs to stdout
)


def get_list_params(path_to_json):
    """extract important parameters about the given list.json"""
    file_exists = path_to_json.exists()
    if file_exists:
        list_json = json.load(open(path_to_json, "r"))

    params = {
        "exists": file_exists,
        "path": path_to_json if file_exists else None,
        "folder": path_to_json.parts[-2] if file_exists else None,
        "version": list_json.get("version", None) if file_exists else None,
        "content": set(list_json.get("list", [])) if file_exists else set(),
        "valid": validator.validate_json(list_json) if file_exists else None,
    }
    return params


def determine_categories(lists_dir_source, lists_dir_target):
    """ Determinate category for each list.json in the source directory.
    It passes through the all 'lists.json' in 'lists_dir_source' and compares them with the related lists in 'lists_dir_target'
    """
    list_category = []
    for path in Path(lists_dir_source).iterdir():
        if (not path.is_dir()) or (not path.joinpath("list.json").exists()):
            continue

        source = get_list_params(path.joinpath("list.json"))
        target = get_list_params(Path(lists_dir_target).joinpath(path.name, "list.json"))

        try:
            cmp_version = 1 if (source["version"] > target["version"]) else -1 if source["version"] < target["version"] else 0
        except TypeError:
            cmp_version = None
        same_content = False if source["content"].symmetric_difference(target["content"]) else True
        category = get_category_code(target["exists"], cmp_version, same_content, source["valid"])

        list_category.append((source, category))

    return list_category


def get_category_code(target_exists, cmp_version, same_content, source_valid):
    if not target_exists:
        category = "XV" if source_valid else "XI"
    else:
        cmp_version_code = {1: "H", 0: "S", -1: "L", None: "I"}
        same_content_code = {True: "S", False: "D"}
        source_valid_code = {True: "V", False: "I"}
        category = cmp_version_code[cmp_version]+same_content_code[same_content]+source_valid_code[source_valid]
    return category


def get_category_desc(category_code: str) -> str:
    """returns text description of the given category.
    Example: HSV -> (HIGHER VERSION; SAME SET OF INDICATORS; VALID INDICATORS)
    """
    cmp_version_txt = {"H": "HIGHER VERSION", "S": "SAME VERSION", "L": "LOWER VERSION", "I": "INCOMPARABLE VERSION"}
    same_content_txt = {"S": "SAME SET OF INDICATORS", "D": "DIFFERENT SET OF INDICATORS"}
    source_valid_txt = {"V": "VALID INDICATORS", "I": "INVALID INDICATORS"}
    if category_code.startswith("X"):
        text = f"(TARGET DOES NOT EXISTS; {source_valid_txt[category_code[-1]]})"
    else:
        text = f"({cmp_version_txt[category_code[0]]}; {same_content_txt[category_code[1]]}; {source_valid_txt[category_code[2]]})"
    return text


def print_all_categories():
    """ just prints all possible categories with their codes and descriptions """
    for source_valid in [True, False]:
        cat = get_category_code(False, None, None, source_valid)
        cat_desc = get_category_desc(cat)
        print(f"[{cat}] {cat_desc}")

    for cmp_version in [1, 0, -1, None]:
        for same_content in [True, False]:
            for source_valid in [True, False]:
                cat = get_category_code(True, cmp_version, same_content, source_valid)
                cat_desc = get_category_desc(cat)
                print(f"[{cat}] {cat_desc}")


def print_lists_diff(source_path, target_path):
    raise NotImplementedError
    source = get_list_params(source_path)
    target = get_list_params(target_path)
    lists_diff = f"human-readable differences between {source_path} and {target_path}"
    print(lists_diff)
    return lists_diff


def print_merge_info(list_category):
    """prints summary of the states (categories) of the current lists"""
    info = {}
    for list_, category in list_category:
        desc = f"[{category}] {get_category_desc(category)}"
        lists = info.get(desc, [])
        lists.append(list_)
        info[desc] = lists

    for msg in sorted(info.keys()):
        print(msg)
        for f in sorted([f["folder"] for f in info[msg]]):
            print("-", f)
        print()


def main():
    arg_parser = argparse.ArgumentParser(description="Merge")
    arg_parser.add_argument("--info",
                            action="store_true",
                            help="only prints info and does not merge anything")
    arg_parser.add_argument("--warninglists",
                            action="store",
                            choices=['misp', 'tsec'],
                            help="which warninglists should be merged",
                            type=str.lower)
    args = arg_parser.parse_args()

    config = configparser.ConfigParser()
    config.read("config.ini")

    lists_dir_target = "./lists/"

    if args.warninglists == "misp":
        lists_dir_source = "./misp-warninglists/lists/"
        merge_categories = [c.strip() for c in config["MISP-WARNINGLISTS"]["merge_categories"].split(",")]
        warning_categories = [c.strip() for c in config["MISP-WARNINGLISTS"]["warning_categories"].split(",")]
    elif args.warninglists == "tsec":
        lists_dir_source = "./tsec-warninglists/lists/"
        merge_categories = [c.strip() for c in config["TSEC-WARNINGLISTS"]["merge_categories"].split(",")]
        warning_categories = [c.strip() for c in config["TSEC-WARNINGLISTS"]["warning_categories"].split(",")]

    # this determines category for each list.json in _lists_dir_source_
    list_category = determine_categories(lists_dir_source, lists_dir_target)

    if args.info:  # print info about all the list.json in source directory
        print(f">> Summary info about all the 'list.json' available in {lists_dir_source}\n")
        print_merge_info(list_category)
        exit()

    for source, category in list_category:
        target_path = Path(lists_dir_target).joinpath(source["folder"])
        log_msg = {"folder": source['folder'],
                   "source": str(source["path"]),
                   "version": source["version"],
                   "n_indicators": len(source["content"]),
                   "merge_category_code": category,
                   "merge_category_desc": str(get_category_desc(category))}

        log_proper_level = logger.warning if category in warning_categories else logger.info

        if category in merge_categories and len(source["content"]) > 0:
            if not target_path.exists():
                os.makedirs(target_path)
            shutil.copy2(source["path"], target_path.joinpath("list.json"))
            log_proper_level(f"List merged {log_msg}")  # logging
        else:
            log_proper_level(f"List not merged {log_msg}")  # logging


if __name__ == "__main__":
    log_msg = {"sys_argv": sys.argv, "python": sys.version}
    logger.info(f"start {log_msg}")

    try:
        main()
    except Exception as e:
        print(traceback.print_exc())
        error_msg = {'exception': repr(e), 'traceback': traceback.format_exc()}
        logger.critical(f"finished with error {error_msg}")
    else:
        logger.info(f"finished successfully")


