# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 14:22:18 2020
Download m3u8 file, just use code ‘python download_m3u8_v2.py’ in the commond windows to download movie files
We have open multiplystread for speeding up
@author: XL
"""
import os 
import requests
#import sys
from multiprocessing.pool import Pool
from functools import partial
from tqdm import tqdm

headers = {
   'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chro\
me/74.0.3729.108 Safari/537.36"}

file_dir_main = os.getcwd()
file_dir1 = os.path.join(file_dir_main, 'movies')
if not os.path.exists(file_dir1):
    os.mkdir(file_dir1)


class M3u8_class():
    def __init__(self, url):
        self.url = url
        self.url_list = []
        self.url_name = []
        self.url_all = url.split('/')
        self.file_name = self.url_all[-2]
        self.base_url = '/'.join(self.url_all[:-1])

    def para_m3u8(self, url=None, base_url=None):
        if url == None:
            url = self.url
        if base_url==None:
            base_url = self.base_url
        try:
            m3u8_result = requests.get(url, headers = headers)
        except Exception as e:
            print(e)
            exit()
        if m3u8_result.status_code != 200:
            print('无效的url：', m3u8_result.status_code)
            exit()
        else:
            self.m3u8_content = m3u8_result.content.decode('utf8')
        if '#EXTM3U' not in self.m3u8_content:
            print('Not a m3u8 url!')
            return None
        content = self.m3u8_content.split('\n')
        for i in content:
            if '.ts' in i:
                split_i_url = i.split('/')
                self.url_name.append(split_i_url[-1])
                self.url_list.append(base_url+'/'+split_i_url[-1])
            elif '.m3u' in i:
                self.new_m3u(i)
                
    def new_m3u(self, new_url_part):
        temp = new_url_part.split('/')
        new_url_list = self.url_all[:-1]
        for i in temp:
            if not i  in self.url_all[:-1]:
                new_url_list.append(i)
        new_url =  '/'.join(new_url_list)
        new_base_url = '/'.join(new_url_list[:-1])
        self.para_m3u8(new_url, new_base_url)


class Ts_class():
    def __init__(self, url, name, number, file_dir_ts):
        self.url = url
        self.name = name
        self.number = number
        self.file_dir_ts = file_dir_ts
        self.file_dir = os.listdir(file_dir_ts)
        self.content = b''

    def get(self, num):
        if self.name in self.file_dir:
            with open(os.path.join(self.file_dir_ts, self.name), 'rb') as f:
                self.content = f.read()
        else:
            ts_res = requests.get(self.url, headers)
            if ts_res.status_code != 200:
                print('Fail to download {}'.format(self.url))
                return None
            self.content = ts_res.content
        # sys.stdout.write('%.4f finished!\r'  %float((self.number+1)/num*100))
        # sys.stdout.flush()
       # print('%.4f finished!' %float((self.number+1)/num*100))
        return None

    def save(self):
        if self.name in self.file_dir:
            print('file %s already exists!' % self.name)
        else:
            if self.content:
                with open(os.path.join(self.file_dir_ts, self.name), 'wb') as f:
                    f.write(self.content)
            else:
                print("file %s doesn't exist!" % self.name)
                return None
   
def download(url_name, f_dir='a', num_all=999):
    ts = Ts_class(url_name[0], url_name[1], url_name[2], f_dir)
    ts.get(num_all)
    return ts


def clear_ts(dir_remove_ts):
    file_list_ts = os.listdir(dir_remove_ts)
    for f_n in file_list_ts:
        if '.ts' in f_n:
            os.remove(os.path.join(dir_remove_ts, f_n))



def save_mp4(mv_list, file_name, movie_file_dir):
    file_path = os.path.join(movie_file_dir, file_name+'.mp4')
    if len(mv_list)==[]:
        print("Didn't download any movies!")
        return None
    if None in mv_list:
        print("You lost some ts file.Please try again!")
        mv_real = [i for i in mv_list if i]
        for ts in mv_real:
            ts.save()
        return None
    mv_list.sort(key=lambda x: x.number)
    for ts_c in mv_list:
        with open(file_path, 'ab') as f:
            f.write(ts_c.content)
    clear_ts(movie_file_dir)


def main():
    m3u8_url = input('Please input the m3u8 url:\n').strip()
    'http://cn2.5311444.com/hls/20181031/8e1f5a33ca8462638ed00ad92d354465/1540960119/index.m3u8'
    m3 = M3u8_class(m3u8_url)
    m3.para_m3u8()

    movie_file_dir = os.path.join(file_dir1, m3.file_name)
    if not os.path.isdir(movie_file_dir):
        os.mkdir(movie_file_dir)

    ts_list = [[m3.url_list[i], m3.url_name[i], i] for i in range(len(m3.url_list))]

    partial_func = partial(download, f_dir=movie_file_dir, num_all=len(m3.url_list))
    # for i in range(num_url):
    #     mv_list.append(p.apply_async(download_file, (url_list1[i], target_url, num_url,)).get())
    print('-------------start-------------')
    p = Pool(10)
    # mv_list = p.map(partial_func,  ts_list)  # 多进程返回的mv_list是一个返回值组成的列表
    mv_list = list(tqdm(p.imap(partial_func, ts_list), total=len(m3.url_list), desc='downloading ts', ascii=True))
    p.close()
    p.join()
    save_mp4(mv_list, m3.file_name, movie_file_dir)
    print('------------finished-----------')
    
if __name__ == '__main__':
    main()
