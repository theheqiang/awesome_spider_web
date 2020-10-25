# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : He Qiang
from functools import reduce
import time
import requests
import execjs

ctx = execjs.compile(open('encrypted_pos.js', encoding='utf8').read())


headers = {
    'Proxy-Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://match.yuanrenxue.com/match/1',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

total = 0

for i in range(1, 6):
    raw_ts = int(time.time())
    m = ctx.call('hex_md5', str(raw_ts * 1000))
    params = (
        ('page', i),
        ('m', m + '丨' + str(raw_ts)),
    )

    response = requests.get('http://match.yuanrenxue.com/api/match/1', headers=headers, params=params,
                            verify=False)
    total += sum([item['value'] for item in response.json()['data']])


print(total//50)