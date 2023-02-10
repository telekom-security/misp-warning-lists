#!/usr/bin/env python3
import json
import datetime as dt

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file


def process(file, dst):
    warninglist = {
        'name': "List of the official Googlebot IP ranges",
        'version': '',
        'description': "List of the official Googlebot IP ranges (https://developers.google.com/search/docs/crawling-indexing/verifying-googlebot)",
        'type': "cidr",
        'list': [],
        'matching_attributes': ["ip-dst", "ip-src", "domain|ip"]
    }

    with open(get_abspath_source_file(file), 'r') as f:
        ips_json = json.load(f)
    for ips in ips_json.get("prefixes", []):
        for prefix, ip in ips.items():
            if prefix in ["ipv4Prefix", "ipv6Prefix"]:
                warninglist['list'].append(ip.strip())

    try:
        creation_time = ips_json["creationTime"]
        creation_time = dt.datetime.fromisoformat(creation_time)
    except (KeyError, ValueError):
        warninglist['version'] = get_version()
    else:
        warninglist['version'] = creation_time.strftime('%Y%m%d')

    write_to_file(warninglist, dst)
    return warninglist


if __name__ == "__main__":
    url = "https://developers.google.com/static/search/apis/ipranges/googlebot.json"
    file = "googlebot.json"
    dst = "googlebot"

    download_to_file(url, file)
    process(file, dst)
