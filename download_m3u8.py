# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 14:22:18 2020
Download m3u8 file, just use code ‘python download_m3u8.py’ in the commond windows to download movie files
We have open multiplystread for speeding up
@author: XL
"""
import os 
import requests
from multiprocessing.pool import Pool
from functools import partial

headers = {
   'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
                 "AppleWebKit/537.36 (KHTML, like Gecko) "
                 "Chrome/72.0.3626.109 Safari/537.36",
           }

def get_m3u8_content():
    m3u8_url = input('Please input the m3u8 url:\n').strip()
    'http://meng.wuyou-zuida.com/20200111/25283_0d1ac929/1000k/hls/index.m3u8'
    split_m3u8_url = m3u8_url.split('/')
    file_name = split_m3u8_url[-2]
    target_url = '/'.join(split_m3u8_url[:-1])
    m3u8_result = requests.get(m3u8_url, headers=headers)
    if m3u8_result.status_code != 200:
        print('无效的url：', m3u8_result.status_code)
        return None
    else:
        m3u8_content = m3u8_result.content.decode('utf8')
        return m3u8_content, target_url,file_name

def para_m3u8(m3u8_content):
    if '#EXTM3U' not in m3u8_content:
        print('Not a m3u8 url!')
        return None
    content = m3u8_content.split('\n')
    url_list = []
    for i in content:
        if '.ts' in i:
            url_list.append(i)
    return url_list
    
    
def download_file(url_list, target_url, num):
    global num_d
    point = '.'*30
    equal = '='*30
    mid = int(30*int(url_list[0])/num)
    disp = equal[:mid]
    if not mid == 30:
        node = '>'
    else:
        node = ''
    disp = equal[:mid]+node+point[:30-mid]
    ts_res = requests.get(target_url + '/' + url_list[1], headers)
    if ts_res.status_code != 200:
        print('Fail to download {}'.format(target_url+'/'+url_list[1]))
        return None
    print('Downloading {} [{}]'.format(url_list[1], disp))
    num_d = num_d + 1
    return [url_list[0], ts_res.content]

def download_file_v2(url_list, target_url, num):
    point = '.'*30
    equal = '='*30
    mid = int(30*int(url_list[0])/num)
    if not mid == 30:
        node = '>'
    else:
        node = ''
    disp = equal[:mid]+node+point[:30-mid]
    ts_res = requests.get(target_url + '/' + url_list[1], headers)
    if ts_res.status_code != 200:
        print('Fail to download {}'.format(target_url+'/'+url_list[1]))
        return None
    print('Downloading {} [{}]'.format(url_list[1], disp))

    file_dir = os.getcwd()
    file_dier1 = os.path.join(file_dir, 'movies')
    if  not os.path.exists(file_dier1):
        os.mkdir(file_dier1)
    file_path = os.path.join(file_dier1, url_list[1])
    with open(file_path, 'wb') as f:
        f.write(ts_res.content)

def save_mp4(mv_list, file_name):
    file_dir = os.getcwd()
    file_dier1 = os.path.join(file_dir, 'movies')
    if  not os.path.exists(file_dier1):
        os.mkdir(file_dier1)
    file_path = os.path.join(file_dier1, file_name+'.mp4')
    with open(file_path, 'wb') as f:
        for i in range(len(mv_list)):
            for j in mv_list:
                if i == j[0]:
                    f.write(j[1])

def main():
    m3u8_content, target_url, file_name = get_m3u8_content()
    url_list = para_m3u8(m3u8_content)
    url_list1 = []
    for i, j in enumerate(url_list):
        url_list1.append([i, j])
    p = Pool()
    num_url = len(url_list1)
    mv_list = []
    partial_func = partial(download_file, target_url=target_url, num=num_url)
    # for i in range(num_url):
    #     mv_list.append(p.apply_async(download_file, (url_list1[i], target_url, num_url,)).get())
    print('-------------start-------------')
    p.map(partial_func, url_list1)
    p.close()
    p.join()
    save_mp4(mv_list, file_name)
    print('-------------end-------------')
    
if __name__ == '__main__':
    main()
