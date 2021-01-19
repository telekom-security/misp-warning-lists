#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import datetime
import json

url = 'https://www.internic.net/domain/named.root'

user_agent = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0'}

r = requests.get(url, headers=user_agent, timeout=600)

rootdns_warninglist = {}
version = int(datetime.date.today().strftime('%Y%m%d'))

rootdns_warninglist['description'] = "Contains DNS root servers"
rootdns_warninglist['version'] = version
rootdns_warninglist['name'] = "Root DNS servers"

# Collect data
ips = []
domains = []

for line in r.text.split('\n'):
    record_line = line.split()
    if len(record_line) != 4:
        continue

    if record_line[2] == 'NS':
        record = record_line[3].lower().strip('.')
        domains.append(record)

    if record_line[2] == 'A':
        record = record_line[3]
        ips.append(record)

# Write data

rootdns_warninglist['type'] = 'ip'
rootdns_warninglist['list'] = ips
rootdns_warninglist['matching_attributes'] = ['ip-src', 'ip-dst']

with open('../lists/root-dns-ipv4/list.json', 'w') as data_file:
    json.dump(rootdns_warninglist, data_file, indent=4, sort_keys=True)

rootdns_warninglist['type'] = 'hostname'
rootdns_warninglist['list'] = domains
rootdns_warninglist['matching_attributes'] = ['domain', 'hostname']

with open('../lists/root-dns-hostname/list.json', 'w') as data_file:
    json.dump(rootdns_warninglist, data_file, indent=4, sort_keys=True)
