#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import datetime
import urllib.request
import json
import requests

r = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json', timeout=600)

j = json.loads(r.text)

l = []

for prefix in j['prefixes']:
   l.append(prefix['ip_prefix'])

for prefix in j['ipv6_prefixes']:
   l.append(prefix['ipv6_prefix'])

warninglist = {}
warninglist['name'] = 'List of known Amazon AWS IP address ranges'
warninglist['version'] = int(datetime.date.today().strftime('%Y%m%d'))
warninglist['description'] = 'Amazon AWS IP address ranges (https://ip-ranges.amazonaws.com/ip-ranges.json)'
warninglist['type'] = 'cidr'
warninglist['list'] = sorted(set(l))
warninglist['matching_attributes'] = ["ip-src", "ip-dst", "domain|ip"]

print(json.dumps(warninglist))
