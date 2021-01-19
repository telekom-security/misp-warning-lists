#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import datetime
import json
import csv
import os

# TODO: Include MozRank

moz_url_domains = "https://moz.com/top-500/download/?table=top500Domains"

moz_file_domains = "/tmp/top500.domains.csv"

user_agent = {"User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0"}

rDomains = requests.get(moz_url_domains, headers=user_agent, timeout=600)

open(moz_file_domains, 'wb').write(rDomains.content)

moz_warninglist = {}
version = int(datetime.date.today().strftime('%Y%m%d'))

moz_warninglist['description'] = "Event contains one or more entries from the top 500 of the most used domains (Mozilla)."
d = datetime.datetime.now()
moz_warninglist['version'] = version
moz_warninglist['name'] = "Top 500 domains and pages from https://moz.com/top500"
moz_warninglist['type'] = 'hostname'
moz_warninglist['list'] = []
moz_warninglist['matching_attributes'] = ['hostname', 'domain', 'uri', 'url']

with open(moz_file_domains) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            #print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            #print(f'\t{row[0]}. {row[1]}, MozTrust: {row[5]}.')
            v = row[1]
            moz_warninglist['list'].append(v.rstrip().rstrip('/'))
            line_count += 1


moz_warninglist['list'] = sorted(set(moz_warninglist['list']))
print(json.dumps(moz_warninglist))

try:
    os.remove(moz_file_domains)
except:
    print(f'Perhaps {moz_file_domains} does not exist.')
