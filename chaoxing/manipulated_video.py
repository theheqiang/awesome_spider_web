# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : He Qiang

import hashlib
import os
import re
import time
from urllib.parse import urljoin
from io import BytesIO

import requests
from PIL import Image
from lxml import etree
from lxml.html import tostring


class ChaoXing(object):

    def generate_ts(self):
        '''
        生成时间戳
        :return: js里的时间戳
        '''
        return int(time.time()) * 1000

    def get_courses_data(self, header, base_url, all_cookie):
        '''

        :param header: 请求头
        :param base_url: 用户首页接口
        :param all_cookie: 请求cookie
        :return:
        '''
        header[
            'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
        header['Host'] = 'i.chaoxing.com'
        # 请求下面这个链接，自动重定向到url：http://i.chaoxing.com/base?t=1589036774406 获取课程选择页面参数
        base_response = requests.get(
            url=base_url,
            headers=header,
            cookies=all_cookie,
            timeout=10
        )
        all_cookie.update(base_response.cookies.get_dict())
        # param: interaction?s=f94269a49525d8a229c414861fbbd65c
        param = re.findall(r"(.*)visit/(.*)',this", base_response.text)[0][1]

        visit_url = 'http://mooc1-1.chaoxing.com/visit/' + param
        header['Host'] = 'mooc1-1.chaoxing.com'
        header['Referer'] = 'http://i.chaoxing.com/base?t={}'.format(self.generate_ts())
        # 请求课程选择页面
        visit_response = requests.get(
            url=visit_url,
            headers=header,
            cookies=all_cookie,
            timeout=10
        )
        all_cookie.update(visit_response.cookies.get_dict())

        course_dict = {}
        tree = etree.HTML(visit_response.text)
        li_list = tree.xpath('/html/body/div/div[2]/div[3]/ul/li')
        li_list.pop()
        print('序号', '    课程名称')
        for index, li in enumerate(li_list, start=1):
            course_url = 'https://mooc1-1.chaoxing.com' + li.xpath('./div/a/@href')[0]
            course_title = li.xpath('./div[2]/h3/a/@title')[0]
            course_dict[index] = {'url': course_url, 'title': course_title}
            print(index, '    ' + course_title)

        while 1:
            chose_course = input('请选择你要刷课的序号(q退出):').strip()
            if chose_course.upper() == 'Q':
                break
            try:
                course_url = course_dict.get(int(chose_course)).get('url')
            except:
                print('输入的序号有误,请重新输入')
                continue
            else:
                params = re.findall(r".*courseId=(.*)&clazzid=(.*)&vc=(.*)&cpi=(.*)&enc=(.*)", course_url)

                courseId = params[0][0]
                clazzid = params[0][1]
                cpi = params[0][3]

                course_response = requests.get(
                    url=course_url,
                    headers=header,
                    cookies=all_cookie,
                    timeout=10
                )
                selector = etree.HTML(course_response.text)

                for ii in selector.xpath("//span[@class='articlename']"):
                    # 将byte类型转换为string类型
                    s = bytes.decode(tostring(ii.xpath('./a')[0])).strip()
                    chapter_name = ii.xpath('./a/@title')[0].strip()
                    chapterId = re.findall(r'.*chapterId=(.*)&amp;courseId', s)[0]
                    # 组建章节的url
                    url = 'https://mooc1-1.chaoxing.com/knowledge/cards?' \
                          'clazzid={}&courseid={}&knowledgeid={}&num=0&ut=s&cpi={}&v=20160407-1'.format(clazzid,
                                                                                                        courseId,
                                                                                                        chapterId, cpi)
                    header['Referer'] = course_url
                    cards_response = requests.get(
                        url=url,
                        headers=header,
                        cookies=all_cookie,
                        timeout=10
                    )
                    # print(cards_response.text)
                    # chapter_name = re.findall()
                    try:
                        jobid = re.findall(r'"jobid":"(.*?)"', cards_response.text)[0]
                        otherInfo = re.findall(r'"otherInfo":"(.*?)"', cards_response.text)[0]
                        user_id = re.findall(r'"userid":"(.*?)"', cards_response.text)[0]
                        object_id = re.findall(r'"objectid":"(.*?)"', cards_response.text)[0]
                    except IndexError:
                        continue
                    else:
                        header[
                            'Referer'] = 'https://mooc1-1.chaoxing.com/ananas/modules/video/index.html?v=2020-0430-2139'
                        status_url = 'https://mooc1-1.chaoxing.com/ananas/status/'
                        params = {
                            'k': '',
                            'flag': 'normal',
                            '_dc': self.generate_ts()
                        }
                        video_resp = requests.get(
                            url=urljoin(status_url, object_id),
                            params=params,
                            headers=header,
                            cookies=all_cookie,
                            timeout=10
                        )
                        dtoken = video_resp.json().get('dtoken')
                        duration = video_resp.json().get('duration')

                        manipulating_url = 'https://mooc1-1.chaoxing.com/multimedia/log/a/' + cpi + '/' + dtoken
                        str_format = '[{class_id}][{user_id}][{job_id}][{object_id}][{current_time}][{encrypted_str}][{duration}][{clip_time}]'
                        enc = str_format.format(class_id=clazzid, object_id=object_id,
                                                current_time=duration * 1000, user_id=user_id,
                                                job_id=jobid, encrypted_str='d_yHJ!$pdA~5',
                                                duration=duration * 1000, clip_time='0_{}'.format(duration))
                        md5 = hashlib.md5(enc.encode())
                        encripted_enc = md5.hexdigest()
                        extra_params = (
                            ('clazzId', clazzid),
                            ('playingTime', duration),
                            ('duration', duration),
                            ('clipTime', '0_{}'.format(duration)),
                            ('objectId', object_id),
                            ('otherInfo', otherInfo),
                            ('jobid', jobid),
                            ('userid', user_id),
                            ('isdrag', '0'),
                            ('view', 'pc'),
                            ('enc', encripted_enc),
                            ('rt', '0.9'),
                            ('dtype', 'Video'),
                            ('_t', self.generate_ts()),
                        )
                        final_resp = requests.get(
                            url=manipulating_url,
                            params=extra_params,
                            headers=header,
                            cookies=all_cookie,
                            timeout=10
                        )
                        yield {'name': chapter_name, 'result': final_resp}

    def get_cookie(self, header, base_url):
        '''
            获取登录该网站的cookie
            :param base_url: 该网站的起始网址
            :return: cookie
            '''
        # 存储cookie
        all_cookie = {}
        try:
            # 判断本地是否有cookie.txt文件
            if not os.path.exists('cookie.txt'):
                # 请求超星网址
                base_response = requests.get(
                    url=base_url,
                    headers=header,
                    timeout=10
                )
                # 更新cookie
                all_cookie.update(base_response.cookies.get_dict())

                # uuid = re.findall(r'<input type = "hidden" value="(.*)" id = "uuid"/>', base_response.text)
                # enc = re.findall(r'<input type = "hidden" value="(.*)" id = "enc"/>', base_response.text)
                # quickCode = re.findall(r' <img src="(.*)" id="quickCode">', base_response.text)

                tree = etree.HTML(base_response.text)
                uuid = tree.xpath('//input[@id="uuid"]/@value')
                enc = tree.xpath('//input[@id="enc"]/@value')
                quickCode = tree.xpath('//img[@id="quickCode"]/@src')

                code_url = 'https://passport2.chaoxing.com'

                page_resource = requests.get(url=code_url + quickCode[0], timeout=10).content

                im = Image.open(BytesIO(page_resource))
                # 显示二维码
                im.show()

                # 等待扫码
                state = input('扫码完成？ Y/N\n')
                if state is 'Y':
                    # 1. 扫完码请求登录链接
                    passport_url = 'https://passport2.chaoxing.com/getauthstatus'  # 更新header
                    header['Accept'] = 'application/json, text/javascript, */*; q=0.01'
                    header['Host'] = 'passport2.chaoxing.com'
                    header['Origin'] = 'https://passport2.chaoxing.com'
                    header[
                        'Referer'] = 'https://passport2.chaoxing.com/login?fid=&newversion=true&refer=http%3A%2F%2Fi.chaoxing.com'

                    data = {
                        'enc': enc,
                        'uuid': uuid
                    }

                    passport_response = requests.post(
                        url=passport_url,
                        headers=header,
                        data=data,
                        cookies=all_cookie,
                        timeout=10
                    )
                # 更新cookie
                all_cookie.update(passport_response.cookies.get_dict())
                # 可以在这里将cookie信息保存，在以后的运行中就不用扫码了
                f = open("cookie.txt", 'w')
                f.write(str(all_cookie))
                f.close()
            else:
                # 本地已经有cookie.txt, 读取cookie
                f = open("cookie.txt", 'r')
                all_cookie = eval(f.read())
                f.close()
        except:
            # 请求超时
            print('请求cookie文件超时')

        return all_cookie

    def run(self):
        '''
        启动函数
        :return:
        '''

        base_url = 'http://i.chaoxing.com'
        header = {
            'User-Agent': 'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
        }
        all_cookie = self.get_cookie(header, base_url)

        iterable_data = self.get_courses_data(header, base_url, all_cookie)

        for single in iterable_data:
            resp_code = single.get('result').status_code
            if resp_code == 200:
                chapter_name = single.get('name')
                print(f"{chapter_name}--刷课成功")
                print('进入倒计时(2分钟),防止超星检测')

            timeLeft = 60 * 2
            while timeLeft > 0:
                print('\r剩余时长:{}秒'.format(timeLeft), end='')
                time.sleep(1)
                timeLeft -= 1


if __name__ == '__main__':
    cx = ChaoXing()
    cx.run()
