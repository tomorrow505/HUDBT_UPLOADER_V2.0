# -*- coding: utf-8 -*-
# Author:tomorrow505

import tkinter as tk
from tkinter import Label, E, Entry, StringVar, Button
import os
from os.path import getsize, join
import time
import configparser
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import json
from time import sleep
import my_bencode
import re
str_list = ['TiB', 'GiB', 'MiB', 'KB', 'B']
USER_DATA_PATH = './conf/config_chrome.json'


class ReseedPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.config_dl = self.controller.config_dl

        self.reseed_path = os.path.join(self.config_dl['cache_path'], 'Reseed')
        if not os.path.isdir(self.reseed_path):
            os.mkdir(self.reseed_path)
        self.config_path = join(self.reseed_path, 'reseed.ini')
        self.torrent_path = ''
        self.qb = ''

        self.var_dir = StringVar()
        self.label_show_info = Label(self, text='目录：', anchor=E)
        self.entry_dir = Entry(self, textvariable=self.var_dir, width=60)

        self.btn_create = Button(self, text='生成配置文件', command=self.mkconfig)

        self.txtContent = tk.scrolledtext.ScrolledText(self, height=23, font=("Helvetica", 10), wrap=tk.WORD)

        self.btn_save = Button(self, text='保存', command=self.saveconfig)

        self.btn_start = Button(self, text='开始', command=self.start_reseed)

        self.var_range = StringVar()
        self.label_range = Label(self, text='区间：', anchor=E)
        self.entry_range = Entry(self, textvariable=self.var_range, width=8)

        self.create_page()

    def create_page(self):
        self.label_show_info.place(x=20, y=25, width=40, height=30)
        self.entry_dir.place(x=60, y=25, width=585, height=30)
        self.btn_create.place(x=655, y=25, width=80, height=30)
        self.txtContent.place(x=25, y=75, width=695, height=470)

        self.btn_save.place(x=80, y=555, width=80, height=30)
        self.btn_start.place(x=560, y=555, width=80, height=30)

        self.label_range.place(x=430, y=555, width=40, height=30)
        self.entry_range.place(x=480, y=557, width=60, height=26)

    def mkconfig(self):
        parser = configparser.ConfigParser()
        all_number = 0

        source_dirs = self.var_dir.get().split(";")
        for dir_ in source_dirs:
            all_number = get_item(dir_, parser, all_number)

        self.config_path = join(self.reseed_path, 'reseed.ini')
        with open(self.config_path, 'w', encoding='utf-8') as configfile:
            parser.write(configfile)

        with open(self.config_path, 'r', encoding='utf-8') as configfile:
            lines = configfile.read().replace('{', '').replace('}', '')
            self.txtContent.insert(tk.INSERT, lines)

    def saveconfig(self):
        items = self.txtContent.get(0.0, tk.END)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write(items)

    def start_reseed(self):

        self.qb = self.controller.qb
        self.torrent_path = join(self.reseed_path, 'torrents')
        if not os.path.isdir(self.torrent_path):
            os.mkdir(self.torrent_path)

        filelist = list(os.listdir(self.torrent_path))
        for file in filelist:
            if os.path.isfile(join(self.torrent_path, file)) and file.endswith('.torrent'):
                os.remove(join(self.torrent_path, file))

        driver_ = get_driver(self.torrent_path)
        parser = configparser.ConfigParser()
        parser.read(self.config_path, encoding='utf-8')

        sections = parser.sections()

        start = int(self.var_range.get().split('-')[0])
        end = int(self.var_range.get().split('-')[1])

        start_index = sections.index(str(start))
        end_index = sections.index(str(end))

        count = 0
        in_use_list = []
        for section in sections[start_index: end_index+1]:
            keyword = parser[section]['search_keyword']
            size = parser[section]['size'].split(' ')[0]
            abs_path = parser[section]['abs_path']
            full_name = parser[section]['full_name']
            download_torrent_by_keyword(keyword=keyword, driver=driver_, size=size)
            
			# 发现有的种子比较大，下载慢，所以要求等待下载完
			sleep(2)
            
            while True:
			    torrents = os.listdir(self.torrent_path)
                if all(torrent.endswith('.torrent') for torrent in torrents):
                    break
                else:
                    sleep(1)

            for torrent in torrents:
                abs_torrent_path = os.path.join(self.torrent_path, torrent)
                if abs_torrent_path.endswith('.torrent') and abs_torrent_path not in in_use_list:
                    if check_if_matched(full_name, abs_torrent_path):
                        os.rename(abs_torrent_path, os.path.join(self.torrent_path, str(count) + '.torrent'))
                        torrent = os.path.join(self.torrent_path, str(count) + '.torrent')
                        torrent_file = open(torrent, 'rb')
                        self.qb.download_from_file(torrent_file, savepath=abs_path, category='自动', skip_checking='true',
                                                   paused='true')
                        in_use_list.append(torrent)
                        torrent_file.close()
                        count = count + 1

        driver_.quit()


def getdirsize(dir_):
    size = 0
    for root, dirs, files in os.walk(dir_):
        size += sum([getsize(join(root, name)) for name in files])
    return size


def get_item(base_dir, parser, all_number):
    items = os.listdir(base_dir)

    # print('当前目录下有%d个项目：' % len(items))
    for item in items:
        # print(all_number, item)
        str_index = 0
        path = os.path.join(base_dir, item)
        if os.path.isdir(path):
            if not os.listdir(path):
                item_str = ''
            else:
                item_str = deal_keyword(item)
                try:
                    size_of_item = getdirsize(path)/1024/1024/1024/1024
                except FileNotFoundError:
                    size_of_item = float('inf')
                while size_of_item < 1:
                    size_of_item = size_of_item * 1024
                    str_index = str_index + 1
        else:
            item_str = item[0: item.rfind('.')].replace('.', ' ')
            item_str = deal_keyword(item_str)
            size_of_item = getsize(path)/1024/1024/1024/1024
            while size_of_item < 1:
                size_of_item = size_of_item * 1024
                str_index = str_index + 1
        timearray = time.localtime(os.path.getatime(path))
        otherstyletime = time.strftime("%Y-%m-%d %H:%M:%S", timearray)

        if item_str:
            parser[all_number] = {
                'full_name': item,
                'search_keyword': item_str,
                'size': '%.2f %s' % (size_of_item, str_list[str_index]),
                'create_time': otherstyletime,
                'abs_path': base_dir
            }
            all_number = all_number + 1

    return all_number


def deal_keyword(string):
    item_str = string.replace('.', ' ')
    item_str = item_str.replace('-', ' ')
    item_str = item_str.replace('DD5 1', ' ')
    item_str = item_str.replace('DD 5 1', ' ')
    item_str = item_str.replace('BluRay', ' ')
    item_str = item_str.replace('x264', ' ')
    item_str = item_str.replace('AAC', ' ')
    item_str = re.sub(' +', ' ', item_str)
    return item_str


def get_driver(savepath):
    with open(USER_DATA_PATH, 'r') as config_file:
        user_data = json.load(config_file)['user_data']
        user_data = '/'.join(user_data.split('\\'))
        user_data = '--user-data-dir=' + user_data
        # print(user_data)
        options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': savepath}
        options.add_experimental_option('prefs', prefs)
        options.add_argument(user_data)
        driver = webdriver.Chrome(executable_path='chromedriver.exe', chrome_options=options)

    return driver


def download_torrent_by_keyword(keyword, driver, size):

    url_ = 'chrome-extension://abkdiiddckphbigmakaojlnmakpllenb/index.html#/search-torrent/{keyword}'.\
        format(keyword=keyword)

    driver.get(url_)
    driver.refresh()
    while True:
        try:
            tag = driver.find_element_by_xpath('//*[@id="inspire"]/div[4]/main/div/div/div/div[1]/div')
            if tag.text.find('搜索完成') >= 0:
                try:
                    number = re.findall('共找到 (\d{1,3}) 条结果', tag.text)
                    number = number[0]
                except:
                    number = 0
                break
        except NoSuchElementException:
            pass
    driver.find_element_by_xpath('//*[@id="inspire"]/div[4]/main/div/div/div/div[2]/div[2]/div[1]/table/thead/tr[1]'
                                 '/th[4]/i').click()
    sleep(0.1*int(number))
    table = driver.find_element_by_xpath('//*[@id="inspire"]/div[4]/main/div/div/div/div[2]/div[2]/div[1]/table')
    table = table.find_element_by_tag_name('tbody')

    trs = table.find_elements_by_tag_name('tr')
    for tr in trs:
        td_list = []
        tds = tr.find_elements_by_tag_name('td')
        for td in tds:
            td_list.append(td.text)
        try:
            if td_list[3].split(' ')[0] == size:
                # print(td_list[0])
                try:
                    a = tds[8].find_element_by_tag_name('a')
                    a.click()
                except NoSuchElementException:
                    try:
                        li = tds[8].find_elements_by_tag_name('i')
                        li[2].click()
                    except WebDriverException:
                        driver.execute_script("arguments[0].scrollIntoView(true);", li[2])
                        li[2].click()
                except WebDriverException:
                    driver.execute_script("arguments[0].scrollIntoView(true);", a)
                    driver.execute_script("window.scrollBy(0, -100)")
                    a.click()
                except Exception as exc:
                    pass
                    # print('错误：', exc)
            else:
                pass
        except IndexError:
            pass
        # td_list.append(a_href)
        # print([td_list[0], td_list[1], td_list[3], td_list[9]])


def check_if_matched(name, torrent_path):
    with open(torrent_path, 'rb') as fh:
        torrent_data = fh.read()
    torrent = my_bencode.decode(torrent_data)
    info = torrent[0][b'info']
    file_dir = info[b'name'].decode('utf-8')

    if file_dir == name:
        return True
    else:
        return False
