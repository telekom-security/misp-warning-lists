#!/usr/bin/env python3

import json
import os
import requests
import datetime

base_url = "https://raw.githubusercontent.com/threatstop/crl-ocsp-whitelist/master/"
uri_list = ['crl-hostnames.txt', 'crl-ipv4.txt', 'crl-ipv6.txt', 'ocsp-hostnames.txt', 'ocsp-ipv4.txt', 'ocsp-ipv6.txt']
wl = dict()
wl['list'] = list()


for uri in uri_list:
    url = base_url + uri
    r = requests.get(url)
    wl['list'].extend(r.text.split('\n'))

wl['type'] = "string"
wl['matching_attributes'] = ["hostname", "domain", "ip-dst", "ip-src", "url", "domain|ip"]
wl['name'] = "CRL Warninglist"
wl['version'] = int(datetime.date.today().strftime('%Y%m%d'))
wl['description'] = "CRL Warninglist from threatstop (https://github.com/threatstop/crl-ocsp-whitelist/)"
wl['list'] = sorted(set(wl['list']))

# Remove empty string
wl['list'].remove('')

print(json.dumps(wl))
