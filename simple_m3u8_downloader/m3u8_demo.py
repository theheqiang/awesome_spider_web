# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, wait
from urllib.parse import urljoin

import requests

finishedNum = 0
allNum = 0
fileList = []
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}


def download(downloadLink, name,lock):
    global finishedNum
    global allNum
    for _ in range(10):
        try:
            print(downloadLink)
            req = requests.get(downloadLink, headers=headers, timeout=15).content
            with open(f"{name}", "wb") as f:
                f.write(req)
                f.flush()
            lock.accuire()
            finishedNum += 1
            print(f"\r{name}下载成功, 总进度{finishedNum // allNum * 100}%")
            lock.release()
            break
        except:
            if _ == 9:
                print(f"{name}下载失败")
            else:
                print(f"{name}正在进行第{_}次重试")


def merge_file(path, name):
    global fileList
    cmd = "copy /b "
    for i in fileList:
        if i != fileList[-1]:
            cmd += f"{i} + "
        else:
            cmd += f"{i} {name}"
    os.chdir(path)
    with open('combine.cmd', 'w') as f:
        f.write(cmd)
    os.system("combine.cmd")
    os.system('del /Q *.ts')
    os.system('del /Q *.cmd')


def downloader(url, name, threadNum):
    global allNum
    global fileList
    print("读取文件信息中...")
    downloadPath = 'Download'
    download_path = Path(downloadPath)
    if not download_path.exists():
        download_path.mkdir()
    # 查看是否存在
    if (download_path / name).absolute().exists():
        print(f"视频文件已经存在，如需重新下载请先删除之前的视频文件")
        return
    first_resp = requests.get(url, headers=headers)
    content = first_resp.text.split('\n')
    if "#EXTM3U" not in content[0].strip():
        raise BaseException(f"非M3U8链接")
    has_m3u8_flag = False
    # .m3u8 跳转
    for video in content:
        if ".m3u8" in video:
            url = urljoin(first_resp.url,video.strip())
            print(url)
            second_resp = requests.get(url, headers=headers)
            content = second_resp.text.split('\n')
            has_m3u8_flag = True
    urls = []
    for index, video in enumerate(content):
        if '#EXTINF' in video:
            downloadLink = urljoin(second_resp.url,content[index+1].strip()) if has_m3u8_flag else urljoin(first_resp.url,content[index+1].strip())
            urls.append(downloadLink)
    allNum = len(urls)
    pool = ThreadPoolExecutor(max_workers=threadNum)
    futures = []
    lock = Lock()
    for index, downloadLink in enumerate(urls):
        ts_path = Path(downloadLink)
        fileList.append(ts_path.name)
        futures.append(pool.submit(download, downloadLink, (download_path / ts_path.name).absolute(),lock))
    wait(futures)
    print(f"运行完成")
    merge_file(download_path.absolute(), name)
    print(f"合并完成")
    print(f"文件下载成功，尽情享用吧")


if __name__ == '__main__':
    videoUrl = str(sys.argv[1])
    print(videoUrl)
    name = str(sys.argv[2])
    threadNum = int(sys.argv[3])
    downloader(videoUrl, name, threadNum)