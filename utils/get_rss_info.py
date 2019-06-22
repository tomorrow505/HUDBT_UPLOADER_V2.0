# -*- coding: utf-8 -*-
# Author:Chengli


import feedparser
import time
import pickle
import re
RSS_PATH = './conf/rss_config.pickle'


class RssLinkHandler:

    def __init__(self):
        self.rss_links = []  # 存储rss链接
        self.entrie_list = []
        self.rss_refresh_time = 10  # 分钟
        self.now_time = ''
        self.last_time = ''

    def load_rss_config(self):
        self.rss_links.clear()
        with open(RSS_PATH, "rb") as rss_file:
            rss_list = pickle.load(rss_file)
            for item in rss_list:
                self.rss_links.append(item[0])

    def get_entries(self, size):
        if not self.now_time:
            self.now_time = time.time()
            self.last_time = self.now_time - int(self.rss_refresh_time)*60
        else:
            self.last_time = self.last_time + int(self.rss_refresh_time)*60
        self.entrie_list.clear()
        self.load_rss_config()
        for rss_link in self.rss_links:
            d = feedparser.parse(rss_link)
            for entrie in d.entries:

                if not judge_size(entrie, size):
                    continue

                tt = entrie['published_parsed']
                time_pub = time.mktime(tt) + 28800
                if time_pub >= self.last_time or (int(self.rss_refresh_time) == 0):
                    # 在规定时间内发布的

                    if d['feed']['title'] == '南洋PT Torrents':
                        entrie['link'] = entrie['link'].replace('http', 'https')

                    if d['feed']['title'] != 'PT@KEEPFRDS Torrents':
                        if str(entrie['summary_detail']['value']).find("禁转") >= 0 or \
                                str(entrie['summary_detail']).find("禁止转载") >= 0:
                            continue
                        else:
                            self.entrie_list.append(dict(entrie))
                    else:
                        self.entrie_list.append(dict(entrie))
        return self.entrie_list

    def change_refresh_time(self, refresh_time):
        self.rss_refresh_time = refresh_time


def judge_size(entrie, size):
    if int(size) == 0:
        return True
    g = re.search('\[(\d.*?) GB\]', entrie['title'])
    try:
        size_ = float(g.group(1))
    except AttributeError:
        size_ = 0
    if size_ > size:
        return False
    else:
        return True

