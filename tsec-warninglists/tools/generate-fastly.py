#!/usr/bin/env python3
import json
import datetime as dt

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file


def process(file, dst):
    warninglist = {
        'name': "List of known Fastly IP address ranges",
        'version': get_version(),
        'description': "Fastly IP address ranges (https://api.fastly.com/public-ip-list)",
        'type': "cidr",
        'list': [],
        'matching_attributes': ["ip-dst", "ip-src", "domain|ip"]
    }

    with open(get_abspath_source_file(file), 'r') as f:
        ips_json = json.load(f)
    for ip in ips_json.get("addresses", []):
        warninglist['list'].append(ip.strip())
    for ip in ips_json.get("ipv6_addresses", []):
        warninglist['list'].append(ip.strip())

    write_to_file(warninglist, dst)
    return warninglist


if __name__ == "__main__":
    url = "https://api.fastly.com/public-ip-list"
    file = "fastly.json"
    dst = "fastly"

    download_to_file(url, file)
    process(file, dst)
