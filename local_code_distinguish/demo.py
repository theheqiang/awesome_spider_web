# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : He Qiang

import ctypes

obj= ctypes.WinDLL("code.dll")


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()





if __name__=="__main__":
    '''
    该本地验证码dll只能识别4位数字,且只能用于python32位调用
    识别率很高,具体自己去测试吧
    '''
    img = get_file_content(r'G:\awesome_spider_web\local_code_distinguish\test.jpg')
    print(type(img))
    dz=obj.ocr(img, len(img))
    print("\n\n\n\n" +str(dz) + "\n\n\n\n")

