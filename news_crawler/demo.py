# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : He Qiang

import requests
import cchardet
import traceback


def downloader(url,timeout=10,headers=None,debug=False,is_bytes=False):
    '''
    下载url对应的内容
    :param url: 要下载的url
    :param timeout: 超时时间
    :param headers: 请求头
    :param debug: 是否debug
    :param is_bytes: 要求数据是否为字节
    :return: 状态码 文本数据 url
    '''
    _headers = {
        'User-Agent':('Mozilla/5.0 (compatible; MSIE 9.0; '
                       'Windows NT 6.1; Win64; x64; Trident/5.0)'),
    }

    if headers is not None:
        _headers = headers

    try:
        r = requests.get(url,timeout=timeout,headers=headers)
        if is_bytes is True:
            html = r.content
        else:
            encoding = cchardet.detect(r.content)['encoding']
            html = r.content.decode(encoding)

        status = r.status_code
        redircted_url = r.url

    except:
        if debug is True:
            traceback.print_exc()

        msg = 'failed to download url:{}'.format(url)

        print(msg)

        if is_bytes is True:
            html = b''
        else:
            html = ''
        status = 0
    return status,html,redircted_url



import re
re.findall()