# -*- coding: utf-8 -*-
# Author:Chengli
import os
import re
import json
import inspect
import requests
import html_handler
import ctypes
import my_bencode
import psutil
import subprocess

AUTHOR = 'tomorrow505'
VERSION = 'V2.0'
THANK_LIST = 'Rach & Lancesaber & Rhilip'


def load_config_dl():
    config_dl__path = './conf/config_dl.json'
    if not os.path.exists(config_dl__path):
        config_dl_tmp = {
            'Max_Size': 0,
            'study_path': '',
            'movie_path': '',
            'carton_path': '',
            'others_path': '',
            'img_path': '',
            'cache_path': '',
            'rss_open': 0,
            'refresh_time': '10',
            'server_open': 0,
            'anony_close': 0,
            'server_port': '',
            'server_ip': ''
        }
        with open(config_dl__path, 'w') as f:
            json.dump(config_dl_tmp, f)
    else:
        try:
            with open(config_dl__path, 'r') as config_file:
                config_dl_tmp = json.load(config_file)
        except Exception as exc:
            print("config_dl.json load failed: %s" % exc)
    return config_dl_tmp


# 定义用来删除线程
def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
    raise SystemError("PyThreadState_SetAsyncExc failed")


# 结合删除线程的函数对线程进行删除操作
def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


def show_info():

    show_str = '''
            help                    呼出帮助菜单
            post detail_link        提交详情页链接进行下载/发布
            get detail_link         提交详情页链接获取下载状态
            cancle detail_link      提交详情页链接取消下载
            exit                    退出
    '''
    return show_str


def load_pt_sites():
    pt_sites = {}
    try:
        with open('./conf/config_sites.json', 'r') as pt_file:
            pt_sites = json.load(pt_file)
    except (FileNotFoundError, Exception):
        pass
    finally:
        return pt_sites


def find_origin_site(url):
    match_site = ''
    pt_sites = load_pt_sites()
    for site in pt_sites.keys():
        domain = pt_sites[site]['domain']
        if ''.join(url.split(' ')).find(domain) >= 0:
            match_site = site
            break
    if match_site == '':
        return 0
    pt_site = pt_sites[match_site]
    return pt_site


def get_id(url):
    if url.find('https://totheglory.im') >= 0:
        id_ = re.search(r'(\d{2,8})', url)
    else:
        id_ = re.search(r'id=(\d{2,8})', url)
    try:
        my_id = id_.group(1)
        # id_info.append('获取id成功')
        # print('获取id成功')
    except Exception as exc:
        # id_info.append('获取id失败！%s' % exc)
        # print('获取id失败！%s' % exc)
        my_id = -1
    return my_id


def get_response(url, cookie):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    session = requests.session()

    session.headers = headers

    response = session.get(url, cookies=cookie)

    return response


def get_download_url(html, pt_site, tid):
    if pt_site['domain'] == 'https://totheglory.im':
        download_url = "{host}/dl/{tid}/{passkey}".format(host=pt_site['domain'], tid=tid, passkey=pt_site['passkey'])
    elif pt_site['domain'] == 'https://hdsky.me':
        download_url = "{host}/download.php?id={tid}&passkey={passkey}".format(host=pt_site['domain'],
                                                                               tid=tid, passkey=pt_site['passkey'])
    elif pt_site['domain'] == 'https://hdchina.org':
        download_url = html_handler.get_hdchina_download_url(html)
    else:
        download_url = "{host}/download.php?id={tid}".format(host=pt_site['domain'], tid=tid)
    return download_url


def parser_torrent(file_path):
    with open(file_path, 'rb') as fh:
        torrent_data = fh.read()
    torrent = my_bencode.decode(torrent_data)
    info = torrent[0][b'info']
    file_dir = info[b'name'].decode('utf-8')
    if b'files' in info.keys():
        biggest = 0
        file_path = ''
        files = info[b'files']
        for file in files:
            new_path = []
            if file[b'length'] > biggest:
                for path in file[b'path']:
                    new_path.append(path.decode('utf-8'))
                if new_path[-1].endswith(('.mp4', '.mkv', '.avi', '.mov', '.rmvb', '.ts')):
                    biggest = file[b'length']
                    file_path = '\\'.join(new_path)
        file_path = file_dir + '\\' + file_path
        return file_path
    else:
        return file_dir


def kill_myself():

    exe = 'HUDBT-UPLOADER-%s.exe' % VERSION

    pids = psutil.pids()

    for pid in pids:
        p = psutil.Process(pid)
        # print('pid-%s,pname-%s' % (pid, p.name()))
        if p.name() == exe:
            cmd = 'taskkill /F /IM %s' % exe
            # os.system(cmd)
            subprocess.call(cmd, shell=True)
            break
