# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : He Qiang

import hashlib
import time

'''
解析一键解析网站post中的sign值
sign 内容格式: 时间戳 + 解析的url地址 + 固定字符串, 进行md5签名
'''

ts = int(time.time())
parse_url = 'http://v.douyin.com/xYrtAo/'
pin_str = '2b7e1fee9e84'

sign = hashlib.md5(f'{ts}{parse_url}{pin_str}'.encode('utf8')).hexdigest()