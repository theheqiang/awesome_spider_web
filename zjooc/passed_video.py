# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : He Qiang

import time
import math
from random import random
from concurrent.futures import ThreadPoolExecutor
from queue import PriorityQueue

import requests

class Zjooc(object):

    url = 'https://www.zjooc.cn/ajax'
    get_video_playing_server = '/learningmonitor/api/learning/monitor/videoPlaying'
    get_pdf_finished_server = '/learningmonitor/api/learning/monitor/finishTextChapter'
    get_student_course_server = '/jxxt/api/course/courseStudent/getStudentCourseChapters'

    def __init__(self, course_id,cookie):
        self.headers = {
            'User-Agent': 'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
            'Cookie': cookie
        }
        self.course_id = course_id

    def get_ajax_time(self):
        '''
        处理获取请求的加密参数,这里用python实现了,原文是js调用
        :return: 加密参数值
        '''
        n = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"
        i = len(n)
        o = ''
        for _ in range(32):
            o += n[math.floor(random() * i)]
        else:
            result = o + str(int(time.time()) * 1000)

        return result

    def get_student_course_info(self):
        '''
        获取课程信息
        :return:课程信息列表
        '''
        ts = self.get_ajax_time()
        student_params = {
            'time': ts,
            'service': self.get_student_course_server,
            'params[pageNo]': '1',
            'params[courseId]': self.course_id,
            'params[urlNeed]': '0'
        }
        try:
            course_info = requests.get(self.url,params=student_params,headers=self.headers).json()
        except Exception as e:
            print(e)
            return None
        else:
            return course_info

    def parse_course_info(self):
        '''
        解析列表中的数据,进行数据清洗
        :return: 已经清洗好的数据列表
        '''
        data = self.get_student_course_info()
        if not data:
            return None
        single_course_list = []
        course_list = data.get('data')
        # 获取每个章节
        for item in course_list:
            # 获取每个小章节的事件节点
            chapter_node = item['children']
            for i in chapter_node:
                children_node = i['children']
                for child in children_node:
                    course_dict = {}
                    course_dict['id'] = child['id']
                    course_dict['name'] = child['name']
                    course_dict['resourceType'] = child['resourceType']
                    if child['resourceType'] == 1:
                        course_dict['vedioTimeLength'] = child['vedioTimeLength']
                    single_course_list.append(course_dict)

        return single_course_list

    def send_modified_data(self,item,q,index):
        '''
        发送视频观看数据,达到秒过的效果
        :param item: 单个chapter的数据
        :param q: 任务队列
        :param index: 权重
        '''
        ts = self.get_ajax_time()
        if item['resourceType'] == 1:
            video_params = {
                'time': ts,
                'service': self.get_video_playing_server,
                'params[chapterId]': item['id'],
                'params[courseId]': self.course_id,
                'params[playTime]': item['vedioTimeLength'],
                'params[percent]': '100'
            }
            result = requests.get(self.url, params=video_params, headers=self.headers).json()
            if result['resultCode'] == 0:
                q.put((index,item['name'] + '的视频''------秒过成功'))
            else:
                q.put((index,item['name'] + '的视频''------秒过失败'))
        else:
            pdf_params = {
                'time': ts,
                'service': self.get_pdf_finished_server,
                'params[chapterId]': item['id'],
                'params[courseId]': self.course_id,
            }
            result = requests.get(self.url, params=pdf_params, headers=self.headers).json()
            if result['resultCode'] == 0:
                q.put((index, item['name'] + '的pdf''------秒过成功'))
            else:
                q.put((index, item['name'] + '的pdf''------秒过失败'))

    def run(self):
        '''
        启动函数
        :return:
        '''
        single_course_list = self.parse_course_info()
        if not single_course_list:
            print('视频数据解析有误,请重新尝试')
            return

        tp = ThreadPoolExecutor(100)
        q = PriorityQueue()

        for index,item in enumerate(single_course_list):
            tp.submit(self.send_modified_data,self,item,q,index)

        tp.shutdown()

        while not q.empty():
            print(q.get()[1])


if __name__ == '__main__':
    zj = Zjooc('course_id','cookie') # cookie要提供在课程页面的cookie,有能力的可以直接模拟登录,我这里就不模拟登陆了
    zj.run()