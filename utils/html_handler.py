# -*- coding: utf-8 -*-
# Author:tomorrow505

'''
处理与网页相关的解析流程
'''


import re
from bs4 import BeautifulSoup
import requests
from html2bbcode.parser import HTML2BBCode
import get_douban_info
from urllib.parse import unquote

judge_list = ['RELEASE NAME', 'RELEASE DATE', 'VIDEO CODE', 'FRAME RATE', 'AUDIO', 'SOURCE', 'BIT RATE',
              'RESOLUTION', 'SUBTITLES', 'FRAMERATE', 'BITRATE', '[IMG]', '视频编码', '帧　　率', '译　　名',
              '主　　演', '海报']  # [IMG]为了留下ourbits图片  视频编码, 帧　　率 保留HDChina， 译名防止把简介用quote框起来 海报是为了保留北邮人的海报


mediainfo_judge = ['RELEASE NAME', 'RELEASE DATE', 'VIDEO CODE', 'FRAME RATE', 'AUDIO', 'SOURCE', 'BIT RATE',
                   'RESOLUTION', 'SUBTITLES', 'FRAMERATE', 'BITRATE', '视频编码', '帧　　率']

good_team = ('TJUPT', 'MTEAM', 'MPAD', 'HDS', 'HDSPAD', 'NYPT', 'FRDS', 'CHD', 'CHDPAD', 'EPIC', 'DRONES', 'AMIABLE',
             'SPARKS', 'CMCT', 'HDCHINA', 'BEAST', 'WIKI', 'CTRLHD', 'TAYTO', 'DON', 'EBP', 'IDE', 'ZQ', 'HIFI',
             'BMF', 'DECIBEL', 'D-ZON3', 'NCMT', 'HANDJOB', 'AO', 'PBK', 'OURTV', 'OURPAD', 'FLETTH', 'MGS', 'PUTAO',
             'NPUPT', 'NTG', 'NGB', 'DOA', 'TTG', 'NTB', 'DANNI', 'LING', 'HDHOME')


type_dict = {
    "电影": [(['华语', '大陆', '中国'], 401), (['欧洲', '北美', '美国', '法国', '瑞典', '英国', '德国', '意大利', '西班牙', '加拿大'], 415),
           (['亚洲', '日本', '韩国', '日韩', '印度', '泰国'], 414), (['香港', '台湾'], 413)],
    "Movie": [(['大陆', 'CN'], 401), (['欧美', 'US/EU'], 415), (['日韩', 'KR', 'JP', 'KR/韩', 'JP/日'], 414),
              (['港台', 'HK/TW'], 413)],
    "剧集": [(['大陆'], 402), (['欧美', '美剧', '英剧', '美国', '法国', '瑞典', '英国', '德国', '意大利', '西班牙', '加拿大'], 418),
           (['日韩', '日剧', '韩剧'], 416), (['港台'], 417)],
    "电视剧": [(['大陆'], 402), (['欧美'], 418), (['亚洲'], 416), (['港台'], 417)],
    "欧美剧": [(['欧美剧'], 418)],
    "日剧": [(['高清日剧', '日剧包'], 416)],
    "韩剧": [(['高清韩剧', '韩剧包'], 416)],
    "大陆港台剧": [(['大陆港台剧'], 402)],
    "TV series": [(['大陆', 'CN'], 402), (['欧美', '法国', '英国', 'US/EU'], 418),
                  (['Kor Drama', 'KR', 'JP', 'Jpn Drama'], 416), (['香港', '台湾', 'HK/TW'], 417)],
    "TV-Episode": [(['大陆', 'CN'], 402), (['欧美'], 418), (['KR/韩', 'JP/日', 'KR', 'JP'], 416), (['港台'], 417)],
    "TV-Pack": [(['大陆', 'CN'], 402), (['欧美'], 418), (['KR/韩', 'JP/日', 'KR', 'JP'], 416), (['港台'], 417)],
    "综艺": [(['大陆'], 403), (['欧美', '美国', '英国'], 421), (['日韩'], 420), (['港台'], 419)],
    "TV-Show": [(['大陆'], 403), (['欧美'], 421), (['KR/韩', 'JP/日'], 420), (['港台'], 419)],
    "音乐": [(['大陆', '港台', '华语'], 408), (['欧美'], 423), (['日韩'], 422),  (['古典'], 424), (['原声'], 425)],
    "Music": [(['CN', 'HK/TW', '华语'], 408), (['US/EU', '欧美'], 423), (['KR', 'JP', '日韩'], 422),
              (['古典'], 424), (['原声'], 425)],
    "动漫": [(['周边'], 429), (['动漫'], 427)],
    "动画": [(['动画'], 427)],
    "Anime": [(['Anime'], 427)],
    "Animation": [(['Animation'], 427)],
    "软件": [(['软件'], 411)],
    "游戏": [(['游戏'], 410)],
    "资料": [(['资料'], 412)],
    "学习": [(['学习'], 412)],
    "Sports": [(['Sports'], 407)],
    "体育": [(['体育'], 407)],
    "紀錄教育": [(['紀錄教育'], 404)],
    "Documentary": [(['Documentary'], 404)],
    "纪录": [(['纪录'], 404)],
    "移动视频": [(['移动视频'], 430)]
}


class HtmlHandler:

    def __init__(self, abbr, html):
        self.site = abbr
        self.html = html
        self.raw_info = {'title': '', 'small_descr': '', 'descr': '', 'url': '', 'douban_info': '',  'recommand': '',
                         'type_': 409, 'nfo': '', 'hash_info': ''}

        self.soup = self.get_soup()

        self.ref_link = {
            'imdb_link': '',
            'url_imdb_for_desc': {},
            'douban_link': ''
        }

        self.parser_html()

    def get_soup(self):
        if self.site == 'ttg':
            self.html = self.html.encode('ISO-8859-1').decode()
        soup = BeautifulSoup(self.html, 'lxml')
        return soup

    def parser_html(self):

        func_dict = {
            'byr': self.parser_html_byr,
            'tjupt': self.parser_html_tjupt,
            'npupt': self.parser_html_npupt,
            'stju': self.parser_html_sjtu,
            'ourbits': self.parser_html_ourbits,
            'cmct': self.parser_html_cmct,
            'nypt': self.parser_html_nypt,
            'mteam': self.parser_html_mteam,
            'hdchina': self.parser_html_hdchina,
            'ttg': self.parser_html_ttg,
            'FRDS': self.parser_html_frds,
            'hdsky': self.parser_html_hdsky
        }
        func_dict[self.site]()

        return self.raw_info

    def get_raw_info(self):
        return self.raw_info

    # 北邮人
    def parser_html_byr(self):

        # 类型很好获取
        type_1 = self.soup.select('#type')[0].get_text()
        type_2 = self.soup.select('#sec_type')[0].get_text()
        type_ = [type_1, type_2]
        self.raw_info['type_'] = get_type_from_info(type_)

        # 简介
        descr = self.soup.find('div', id='kdescr')
        descr = format_mediainfo(self.soup, descr)
        descr = format_descr_byr(descr)
        self.raw_info['descr'] = descr

        # 获取imdb链接和豆瓣信息
        self.get_imdb_douban_link_by_str(descr)
        douban_info = self.get_douban_info()
        self.raw_info['douban_info'] = douban_info
        self.raw_info['url'] = self.ref_link['imdb_link']

        # 主、副标题
        small_descr = self.soup.select('#subtitle')[0].get_text()
        sub_info = to_bbcode(str(self.soup.find('h1', id='share')))
        if len(small_descr) == 0:
            sub_info_1 = re.sub('\[[^\u4e00-\u9fff]+\]|\[|\]', ' ', sub_info)
            sub_info_1 = re.sub("国产|连载|华语|英文|大陆|欧美", "", sub_info_1).replace(' ', '')
            small_descr = sub_info_1
        if self.raw_info['type_'] in [401, 413, 402, 417, 403, 419]:
            tran_name = re.search('◎片　　名　(.*)', self.raw_info['descr'] + self.raw_info['douban_info'])
        else:
            tran_name = re.search('◎译　　名　(.*)', self.raw_info['descr'] + self.raw_info['douban_info'])
        try:
            tran_name = tran_name.group(1).split('/')[0].strip()
            if small_descr.find(tran_name) >= 0:
                pass
            else:
                small_descr = tran_name + ' ' + small_descr
        except AttributeError:
            pass
        self.raw_info['small_descr'] = small_descr.replace('免费', '')

        if self.raw_info['type_'] in [412, 411, 410]:
            sub_info_2 = re.sub('\[|\]', ' ', sub_info)
            sub_info_2 = re.sub(' +', ' ', sub_info_2)
            self.raw_info['title'] = sub_info_2.strip()

        # print(self.raw_info['descr'])

        # hash_info
        hash_info = ''
        no_border_wide = self.soup.select('td .no_border_wide')
        for item in no_border_wide:
            item_str = str(item)
            if item_str.find('Hash码') >= 0:
                hash_info = to_bbcode(item_str).split(':')[-1].strip()
                break
        self.raw_info['hash_info'] = hash_info

        self.raw_info['nfo'] = judge_nfo_existed(self.raw_info['descr'])

    # CMCT
    def parser_html_cmct(self):

        # 主标题
        title = to_bbcode(str(self.soup.find('h1', id='top').get_text()))
        title = re.sub('\[.*?\]', '', title)
        self.raw_info['title'] = ' '.join(title.split('.')).strip()

        # 副标题
        small_descr = self.soup.select('.rowfollow')[1].get_text()
        self.raw_info['small_descr'] = small_descr

        # 类型
        type_ = (self.soup.select('.rowfollow')[4].get_text())
        type_ = ' '.join(type_.split())
        self.raw_info['type_'] = get_type_from_info(type_)

        # 简介
        descr = to_bbcode_use_api(str(self.soup.find('div', id='kdescr')))
        descr = format_descr_cmct(descr)
        self.raw_info['descr'] = descr

        # 获取链接和豆瓣信息
        self.get_imdb_douban_link_by_str(descr)
        douban_info = self.get_douban_info()
        self.raw_info['douban_info'] = douban_info

        self.raw_info['url'] = self.ref_link['imdb_link']

    # HDChina  # 信任的站点
    def parser_html_hdchina(self):

        # 主标题
        title = to_bbcode(str(self.soup.find('h2', id='top').get_text()))
        title = re.sub('\[.*?\]', '', title)
        self.raw_info['title'] = ' '.join(title.split('.')).strip()

        # 副标题
        small_descr = ''
        for line in self.soup.h3.children:
            small_descr = small_descr + line
        self.raw_info['small_descr'] = small_descr

        # 简介
        # descr = to_bbcode_use_api(str(self.soup.find('div', id='kdescr')))
        descr = self.soup.find('div', id='kdescr')
        descr = format_mediainfo(self.soup, descr)
        descr = format_descr_hdchina(descr)
        self.raw_info['descr'] = descr

        # 获取链接和豆瓣信息
        kimdb = to_bbcode(str(self.soup.find('div', id='kimdb')))
        kdouban = to_bbcode(str(self.soup.find('div', id='kdouban')))
        self.get_imdb_douban_link_by_list([descr, kimdb, kdouban])

        # if not title.upper().endswith(good_team):
        #     douban_info = self.get_douban_info()
        # else:
        #     douban_info = ''
        # self.raw_info['douban_info'] = douban_info
        self.raw_info['url'] = self.ref_link['imdb_link']

        # 类型
        try:
            chandi = re.search('◎国　　家　(.*)', self.raw_info['descr'])
            chandi = ''.join(chandi.group(1).split())
        except AttributeError:
            try:
                chandi = re.search('◎产　　地　(.*)', self.raw_info['descr'])
                chandi = ''.join(chandi.group(1).split())
            except AttributeError:
                chandi = ''
        if not chandi:
            try:
                chandi = re.search('◎地　　区　(.*)', self.raw_info['descr'])
                chandi = ''.join(chandi.group(1).split())
            except AttributeError:
                chandi = ''
        type_ = to_bbcode(str(self.soup.select('li[class="right bspace"]')[0]))
        type_ = type_ + chandi
        self.raw_info['type_'] = get_type_from_info(type_)

        # hash_info
        hash_info = to_bbcode(str(self.soup.select('td .file_hash')[0]))
        hash_info = hash_info.split('：')[-1].strip()
        self.raw_info['hash_info'] = hash_info

        self.raw_info['nfo'] = judge_nfo_existed(self.raw_info['descr'])

        # print(self.raw_info['descr'])

    # HDSky    # 信任的站点
    def parser_html_hdsky(self):

        # 主标题
        all_title = to_bbcode(str(self.soup.find('h1', id='top').get_text()))
        title = re.sub('\[.*?\]', '', all_title)
        self.raw_info['title'] = ' '.join(title.split('.')).strip()

        # # 副标题
        small_descr = self.soup.select('.rowfollow')[2].get_text()
        self.raw_info['small_descr'] = small_descr

        # 简介
        descr = self.soup.find('div', id='kdescr')
        descr = format_mediainfo(self.soup, descr)
        descr = format_descr(descr)
        self.raw_info['descr'] = descr

        kimdb = to_bbcode(str(self.soup.find('div', id='kimdb')))
        kdouban = to_bbcode(str(self.soup.find('div', id='kdouban')))
        # 获取链接和豆瓣信息
        self.get_imdb_douban_link_by_list([descr, kimdb, kdouban])

        # 信任的站点
        # if not title.upper().endswith(good_team):
        #     douban_info = self.get_douban_info()
        # else:
        #     douban_info = ''
        # self.raw_info['douban_info'] = douban_info

        self.raw_info['url'] = self.ref_link['imdb_link']

        # 类型
        try:
            chandi = re.search('◎产　　地　(.*)', self.raw_info['descr'])
            chandi = ''.join(chandi.group(1).split())
        except AttributeError:
            try:
                chandi = re.search('◎国　　家　(.*)', self.raw_info['descr'])
                chandi = ''.join(chandi.group(1).split())
            except AttributeError:
                chandi = ''
        if not chandi:
            try:
                chandi = re.search('◎地　　区　(.*)', self.raw_info['descr'])
                chandi = ''.join(chandi.group(1).split())
            except AttributeError:
                chandi = ''
        type_ = self.soup.select('.rowfollow')[3].get_text()
        type_ = type_ + chandi
        self.raw_info['type_'] = get_type_from_info(type_)

        # hash_info
        hash_info = ''
        no_border_wide = self.soup.select('td .no_border_wide')
        for item in no_border_wide:
            item_str = str(item)
            if item_str.find('Hash码') >= 0:
                hash_info = to_bbcode(item_str).split(':')[-1].strip()
                break
        self.raw_info['hash_info'] = hash_info

        # print(hash_info)
        # print(self.raw_info['descr'])
        self.raw_info['nfo'] = judge_nfo_existed(self.raw_info['descr'])

    # Mteam    # 信任的站点
    def parser_html_mteam(self):

        # 主标题
        title = to_bbcode(str(self.soup.find('h1', id='top').get_text()))
        title = title.split('[免費]')[0]
        title = re.sub('\[.*?\]', '', title).strip()
        self.raw_info['title'] = ' '.join(title.split('.'))

        # 副标题
        small_descr = self.soup.select('.rowfollow')[1].get_text()
        self.raw_info['small_descr'] = small_descr

        # 简介
        descr = self.soup.find('div', id='kdescr')
        if title.upper().endswith(('MTEAM', 'MPAD')):
            mode = 0
        else:
            mode = 1
        descr = format_mediainfo(self.soup, descr, mode=mode)
        descr = format_descr_mteam(descr)
        self.raw_info['descr'] = descr

        kimdb = to_bbcode(str(self.soup.find('div', id='kimdb')))
        kdouban = to_bbcode(str(self.soup.find('div', id='kdouban')))
        # 获取链接和豆瓣信息
        self.get_imdb_douban_link_by_list([descr, kimdb, kdouban])

        # if not title.upper().endswith(good_team):
        #     douban_info = self.get_douban_info()
        # else:
        #     douban_info = ''
        # self.raw_info['douban_info'] = douban_info

        self.raw_info['url'] = self.ref_link['imdb_link']

        # 类型
        type_ = (self.soup.select('.rowfollow')[2].get_text())
        self.raw_info['type_'] = get_type_from_info(type_)

        # hash_info
        hash_info = ''
        no_border_wide = self.soup.select('td .no_border_wide')
        for item in no_border_wide:
            item_str = str(item)
            if item_str.find('Hash碼') >= 0:
                hash_info = to_bbcode(item_str).split(':')[-1].strip()
                break
        self.raw_info['hash_info'] = hash_info

        self.raw_info['nfo'] = judge_nfo_existed(self.raw_info['descr'])

    # 蒲公英  # 信任的站点
    def parser_html_npupt(self):

        title = self.soup.find('div', class_='jtextfill')
        title = title.get_text().split('    ')[0]
        title = ' '.join(title.split('.')).strip()
        self.raw_info['title'] = title

        # 副标题
        small_descr = self.soup.find('span', class_='large').get_text()
        self.raw_info['small_descr'] = small_descr

        # 类型
        info_1 = self.soup.find(class_='label label-success').get_text()
        info_2 = self.soup.find(class_='label label-info').get_text()
        self.raw_info['type_'] = get_type_from_info(info_1 + info_2)

        # 简介
        ads = self.soup.find_all('div', class_='well small')
        try:
            for ad in ads:
                ad.decompose()
        except Exception:
            pass
        descr = self.soup.find('div', id='kdescr')
        descr = format_mediainfo(self.soup, descr, mode=2)
        descr = format_descr_npupt(descr)
        self.raw_info['descr'] = descr

        # 获取链接和豆瓣信息
        self.get_imdb_douban_link_by_str(descr)

        # if not title.upper().endswith(good_team):
        #     douban_info = self.get_douban_info()
        # else:
        #     douban_info = ''
        # self.raw_info['douban_info'] = douban_info

        self.raw_info['url'] = self.ref_link['imdb_link']

        self.raw_info['nfo'] = judge_nfo_existed(self.raw_info['descr'])

        # print(self.raw_info['descr'])

    # 南洋
    def parser_html_nypt(self):

        # 主标题
        title = self.soup.find('h1', id='top').get_text()
        title = title.split(' ')[0]
        self.raw_info['title'] = ' '.join(title.split('.')).strip()

        # # 副标题
        small_descr = self.soup.select('.rowfollow')[1].get_text()
        self.raw_info['small_descr'] = small_descr

        # 简介
        descr = self.soup.find('div', id='kdescr')
        if title.upper().endswith('NYPT'):
            mode = 0
        else:
            mode = 1
        descr = format_mediainfo(self.soup, descr, mode=mode)
        descr = format_descr(descr)
        self.raw_info['descr'] = descr

        kimdb = to_bbcode(str(self.soup.find('div', id='kimdb')))
        kdouban = to_bbcode(str(self.soup.find('div', id='kdouban')))

        # 获取链接和豆瓣信息
        no_url_in_descr = False
        self.get_imdb_douban_link_by_str(descr)
        if not self.ref_link['douban_link'] and not self.ref_link['imdb_link']:
            no_url_in_descr = True
        if no_url_in_descr:
            self.get_imdb_douban_link_by_list([kimdb, kdouban])

        if no_url_in_descr:
            douban_info = self.get_douban_info()
        else:
            douban_info = ''

        self.raw_info['descr'] = douban_info + '\n' + self.raw_info['descr']

        self.raw_info['url'] = self.ref_link['imdb_link']

        # 类型
        try:
            chandi = re.search('◎产　　地　(.*)', descr)
            chandi = ''.join(chandi.group(1).split())
        except AttributeError:
            try:
                chandi = re.search('◎国　　家　(.*)', descr)
                chandi = ''.join(chandi.group(1).split())
            except AttributeError:
                chandi = ''
        if not chandi:
            try:
                chandi = re.search('◎地　　区　(.*)', self.raw_info['descr'])
                chandi = ''.join(chandi.group(1).split())
            except AttributeError:
                chandi = ''
        type_ = (self.soup.select('.rowfollow')[2].get_text())
        type_ = ' '.join(type_.split()) + chandi
        self.raw_info['type_'] = get_type_from_info(type_)

        # hash_info
        hash_info = ''
        no_border_wide = self.soup.select('td .no_border_wide')
        for item in no_border_wide:
            item_str = str(item)
            if item_str.find('Hash码') >= 0:
                hash_info = to_bbcode(item_str).split(':')[-1].strip()
                break
        self.raw_info['hash_info'] = hash_info

        # print(hash_info)
        # print(self.raw_info['descr'])
        self.raw_info['nfo'] = judge_nfo_existed(self.raw_info['descr'])

    # OurBits
    def parser_html_ourbits(self):
        # 主标题
        title = self.soup.find('h1', id='top').get_text()
        title = title.split('[免费]')[0]
        title = re.sub('\[.*?\]', '', title)
        self.raw_info['title'] = title.strip()

        # 副标题
        small_descr = self.soup.select('.rowfollow')[1].get_text()
        self.raw_info['small_descr'] = small_descr

        # 简介 返回来的是经过转换的bbcode，直接str就可以了
        descr = self.soup.find('div', id='kdescr')

        descr = str(descr)
        descr = format_descr_ourbits(descr)
        descr = format_descr(descr)
        self.raw_info['descr'] = descr

        # 获取链接和豆瓣信息
        self.get_imdb_douban_link_by_str(descr)

        if not self.ref_link['douban_link'] and not self.ref_link['imdb_link']:
            if not self.ref_link['imdb_link']:
                kimdb = to_bbcode(str(self.soup.find('div', id='kimdb')))
                try:
                    imdb_link = re.search('.*imdb.com/title/(tt\d{5,9})', kimdb)
                    url_imdb_for_desc = {'site': 'douban', 'sid': imdb_link.group(1)}
                    imdb_link = 'https://www.imdb.com/title/' + imdb_link.group(1) + '/'
                    self.raw_info['recommand'] = recommand_for_imdb(imdb_link)
                    self.ref_link['imdb_link'] = imdb_link
                    self.ref_link['url_imdb_for_desc'] = url_imdb_for_desc
                except AttributeError:
                    pass
            if not self.ref_link['douban_link']:
                doubanid = re.search('data-doubanid=(\d{3,10})', self.html)
                try:
                    doubanid = doubanid.group(1)
                except AttributeError:
                    doubanid = ''
                if doubanid:
                    self.ref_link['douban_link'] = 'https://movie.douban.com/subject/%s/' % doubanid
            if self.ref_link['douban_link'] or self.ref_link['imdb_link']:
                douban_info = self.get_douban_info()
            else:
                douban_info = ''
        else:
            douban_info = ''

        self.raw_info['descr'] = douban_info + descr
        self.raw_info['url'] = self.ref_link['imdb_link']

        # 类型
        type_ = (self.soup.select('.rowfollow')[2].get_text())
        type_ = ' '.join(type_.split())
        self.raw_info['type_'] = get_type_from_info(type_)

        self.raw_info['nfo'] = judge_nfo_existed(self.raw_info['descr'])

        # print(self.raw_info['descr'])

    # 葡萄  # 信任的站点
    def parser_html_sjtu(self):

        # 主标题
        title = self.soup.find('h1').get_text()
        title = re.sub(r'\[.*?\]', '', title).strip()
        self.raw_info['title'] = title.strip()

        # 副标题
        small_descr = to_bbcode(str(self.soup.select('td .rowfollow')[2]))
        self.raw_info['small_descr'] = small_descr

        # # 简介
        descr = self.soup.find('div', id='kdescr')
        descr = format_mediainfo(self.soup, descr)
        descr = format_descr(descr)
        self.raw_info['descr'] = descr

        # 获取链接和豆瓣信息
        self.get_imdb_douban_link_by_str(descr)

        # if not title.upper().endswith(good_team):
        #     douban_info = self.get_douban_info()
        # else:
        #     douban_info = ''
        # self.raw_info['douban_info'] = douban_info

        self.raw_info['url'] = self.ref_link['imdb_link']

        # 类型
        type_ = str(self.soup.select('td .rowfollow')[3].get_text())
        type_ = type_.split()[3]
        self.raw_info['type_'] = get_type_from_info(type_)

        # hash_info
        hash_info = ''
        no_border_wide = self.soup.select('td .no_border_wide')
        for item in no_border_wide:
            item_str = str(item)
            if item_str.find('Hash码') >= 0:
                hash_info = to_bbcode(item_str).split(':')[-1].strip()
                break
        self.raw_info['hash_info'] = hash_info

        # print(hash_info)
        # print(self.raw_info['descr'])

        self.raw_info['nfo'] = judge_nfo_existed(self.raw_info['descr'])

    # 北洋园 # 信任的站点
    def parser_html_tjupt(self):

        # 简介
        descr = self.soup.find('div', id='kdescr')
        descr = format_mediainfo(self.soup, descr, mode=0)
        descr = format_descr_tjupt(descr)
        self.raw_info['descr'] = descr

        kimdb = to_bbcode(str(self.soup.find('div', id='kimdb')))
        kdouban = to_bbcode(str(self.soup.find('div', id='kdouban')))
        # 获取链接和豆瓣信息
        self.get_imdb_douban_link_by_list([descr, kimdb, kdouban])

        # douban_info = self.get_douban_info()

        self.raw_info['url'] = self.ref_link['imdb_link']

        # 类型
        info = ''.join(to_bbcode(str(self.soup.select('td .rowfollow')[3])).split())
        try:
            chandi = re.search('◎产　　地　(.*)', self.raw_info['descr'])
            chandi = ''.join(chandi.group(1).split())
        except AttributeError:
            try:
                chandi = re.search('◎国　　家　(.*)', self.raw_info['descr'])
                chandi = ''.join(chandi.group(1).split())
            except AttributeError:
                chandi = ''
        type_ = info + chandi
        self.raw_info['type_'] = get_type_from_info(type_)

        # 副标题
        small_descr = self.soup.select('td .rowfollow')[2].get_text()
        if self.raw_info['type_'] in [401, 413, 402, 417, 403, 419]:
            tran_name = re.search('◎片　　名　(.*)', self.raw_info['descr'] + self.raw_info['douban_info'])
        else:
            tran_name = re.search('◎译　　名　(.*)', self.raw_info['descr'] + self.raw_info['douban_info'])
        try:
            tran_name = tran_name.group(1).split('/')[0].strip()
            if small_descr.find(tran_name) >= 0:
                pass
            else:
                small_descr = tran_name + ' ' + small_descr
        except AttributeError:
            pass

        self.raw_info['small_descr'] = small_descr

        self.raw_info['nfo'] = judge_nfo_existed(self.raw_info['descr'])

        # hash_info
        hash_info = ''
        no_border_wide = self.soup.select('td .no_border_wide')
        for item in no_border_wide:
            item_str = str(item)
            if item_str.find('Hash码') >= 0:
                hash_info = to_bbcode(item_str).split(':')[-1].strip()
                break
        self.raw_info['hash_info'] = hash_info

        # print(self.raw_info['descr'])

    # TTG  # 信任的站点
    def parser_html_ttg(self):

        # 主标题
        all_title = to_bbcode(str(self.soup.find('h1').get_text()))
        title = re.sub('\[.*?\]', '', all_title)
        self.raw_info['title'] = ' '.join(title.split('.')).strip()

        # 副标题
        small_descr = all_title.replace(title, '')
        small_descr = small_descr.replace('[', '')
        small_descr = small_descr.replace(']', '')
        self.raw_info['small_descr'] = small_descr

        # 简介
        descr = self.soup.find('div', id='kt_d')
        quotos = descr.find_all('p', class_='sub')
        try:
            for quoto in quotos:
                quoto.decompose()
        except Exception:
            pass

        descr = format_mediainfo(self.soup, descr, mode=3)
        descr = format_descr(descr)
        self.raw_info['descr'] = descr

        # 获取链接和豆瓣信息
        self.get_imdb_douban_link_by_str(descr)

        # douban_info = self.get_douban_info() 信任的站点

        self.raw_info['url'] = self.ref_link['imdb_link']

        # 类型——可以提取出来
        try:
            chandi = re.search('产.*地(.*)', self.raw_info['descr'])
            chandi = ''.join(chandi.group(1).split())
        except AttributeError:
            try:
                chandi = re.search('国.*家(.*)', self.raw_info['descr'])
                chandi = ''.join(chandi.group(1).split())
            except AttributeError:
                chandi = ''
        if not chandi:
            try:
                chandi = re.search('◎地　　区　(.*)', self.raw_info['descr'])
                chandi = ''.join(chandi.group(1).split())
            except AttributeError:
                chandi = ''
        type_ = to_bbcode(str(self.soup.select('td[valign="top"]')[8].next_sibling.get_text()))
        type_ = type_ + '产地 ' + chandi
        self.raw_info['type_'] = get_type_from_info(type_)

        self.raw_info['nfo'] = judge_nfo_existed(self.raw_info['descr'])

    # FRDS  # 信任的站点
    def parser_html_frds(self):
        # 主标题
        all_title = to_bbcode(str(self.soup.select('.rowfollow')[1].get_text()))
        self.raw_info['title'] = all_title.strip()

        # # 副标题
        sub_title = to_bbcode(str(self.soup.find('h1').get_text()))
        sub_title = re.sub('【|】| \[.*\]', '', sub_title)
        self.raw_info['small_descr'] = sub_title

        # 简介
        descr = self.soup.find('div', id='kdescr')
        descr = format_mediainfo(self.soup, descr)
        descr = format_descr(descr)
        self.raw_info['descr'] = descr

        # 获取链接和豆瓣信息
        self.get_imdb_douban_link_by_str(descr)

        self.raw_info['url'] = self.ref_link['imdb_link']

        try:
            nfo = to_bbcode(str(self.soup.find('div', id='knfo').get_text()))
            if nfo:
                self.raw_info['nfo'] = '\n[quote=iNFO][font=Courier New]%s[/font][/quote]' % nfo
        except Exception:
            pass

        # 类型
        type_ = to_bbcode(str(self.soup.select('.rowfollow')[2].get_text()))
        try:
            chandi = re.search('◎产　　地　(.*)', self.raw_info['descr'])
            chandi = ''.join(chandi.group(1).split())
        except AttributeError:
            try:
                chandi = re.search('◎国　　家　(.*)', self.raw_info['descr'])
                chandi = ''.join(chandi.group(1).split())
            except AttributeError:
                chandi = ''
        if not chandi:
            try:
                chandi = re.search('◎地　　区　(.*)', self.raw_info['descr'])
                chandi = ''.join(chandi.group(1).split())
            except AttributeError:
                chandi = ''
        type_ = type_ + chandi
        self.raw_info['type_'] = get_type_from_info(type_)

        # hash_info
        hash_info = ''
        no_border_wide = self.soup.select('td .no_border_wide')
        for item in no_border_wide:
            item_str = str(item)
            if item_str.find('Hash码') >= 0:
                hash_info = to_bbcode(item_str).split(':')[-1].strip()
                break
        self.raw_info['hash_info'] = hash_info

        if not self.raw_info['nfo']:
            self.raw_info['nfo'] = judge_nfo_existed(self.raw_info['descr'])
        # print(self.raw_info['descr'])

    def get_imdb_douban_link_by_str(self, check_str):
        if not self.ref_link['imdb_link']:
            try:
                imdb_link = re.search('.*imdb.com/title/(tt\d{5,9})', check_str)
                url_imdb_for_desc = {'site': 'douban', 'sid': imdb_link.group(1)}
                imdb_link = 'https://www.imdb.com/title/' + imdb_link.group(1) + '/'
                self.raw_info['recommand'] = recommand_for_imdb(imdb_link)
                self.ref_link['imdb_link'] = imdb_link
                self.ref_link['url_imdb_for_desc'] = url_imdb_for_desc
            except AttributeError:
                pass
        if not self.ref_link['douban_link']:
            try:
                douban_link = re.search('.*douban.com/subject/(\d{5,9})', check_str)
                douban_link = 'https://movie.douban.com/subject/' + douban_link.group(1) + '/'
                self.ref_link['douban_link'] = douban_link
            except AttributeError:
                pass

    def get_imdb_douban_link_by_list(self, check_list):
        for check_str in check_list:
            if check_str:
                self.get_imdb_douban_link_by_str(check_str)

    def get_douban_info(self):
        if self.ref_link['douban_link']:
            try:
                douban_info = get_douban_info.get_douban_descr(self.ref_link['douban_link'])
                if not self.ref_link['imdb_link']:
                    self.get_imdb_douban_link_by_str(douban_info)
            except Exception:
                douban_info = ''
        else:
            if self.ref_link['url_imdb_for_desc']:
                try:
                    douban_info = get_douban_info.get_douban_descr(self.ref_link['url_imdb_for_desc'])
                except Exception:
                    douban_info = ''
            else:
                douban_info = ''

        return douban_info


# 根据imdb获取推荐
def recommand_for_imdb(url):

    base_command = 'https://api.douban.com/v2/movie/imdb/{tt}?&apikey=02646d3fb69a52ff072d47bf23cef8fd'

    recommand_list = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    session = requests.session()

    session.headers = headers

    response = session.get(url)

    html = response.text
    # print(html)

    before = '[url=https://hudbt.hust.edu.cn/torrents.php?search='

    # links = re.findall('alt="(.*)" title=.*loadlate="(.*)_AL_.jpg', html)

    links = re.findall('href="/title/(.*)\/\?ref.*\n.*alt="(.*)" title=.*loadlate="(.*)_AL_.jpg', html)

    for link in links:
        if link[2].find('UY190') >= 0 or link[2].find('UX128') >= 0:
            url = base_command.format(tt=link[0])
            response = session.get(url)
            page = response.json()
            # print(page)
            if 'msg' not in page.keys():
                title = page['title']
                alt_tit1e = page['alt_title']
                useful_title = ''
                for ch in title:
                    if u'\u4e00' <= ch <= u'\u9fff':
                        useful_title = title.split('/')[0].strip()
                        break
                if useful_title == '':
                    useful_title = alt_tit1e.split('/')[0].strip()

            else:
                useful_title = link[1]

            # print(useful_title)
            str_ = '%s%s][img]%s_AL_.jpg[/img][/url]' % (before, useful_title, link[2])
            recommand_list.append(str_)
    if not recommand_list:
        return ''
    else:
        return '\n[quote=相关推荐]' + ''.join(recommand_list) + '[/quote]'


def to_bbcode(descr):
    parser = HTML2BBCode()
    bbcode = parser.feed(descr)
    return bbcode


def format_descr_byr(descr):
    tmp = []
    descr = descr.split('\n')
    for line in descr:
        if len(line.strip()) == 0:
            pass
        else:
            tmp.append(line)
    descr = '\n'.join(tmp)
    descr = re.sub('Info Format Powered By @Rhilip', '', descr)
    return descr


def format_descr_cmct(descr):
    tmp = []
    descr = descr.split('\n')
    for line in descr:
        if len(line.strip()) == 0:
            pass
        else:
            tmp.append(line)
    descr = '\n'.join(tmp[3:-7])
    return descr


def get_hdchina_download_url(html):
    soup = BeautifulSoup(html, 'lxml')
    # print(html)
    download_link = soup.find('a', id='clip_target').get_text()
    return download_link


def format_descr(descr):
    tmp = []
    descr = descr.split('\n')
    for line in descr:
        if len(line.strip()) == 0:
            pass
        else:
            tmp.append(line)
    descr = '\n'.join(tmp)
    return descr


def format_descr_ourbits(descr):
    a = '<div id="kdescr"><div class="ubbcode">'
    b = '</div></div>'
    c = '[size=3][color=RoyalBlue][b] MediaInfo[/b][/color]'
    descr = descr.replace(a, '')
    descr = descr.replace(b, '')
    descr = descr.replace(c, '')

    quoto = re.findall('(\[quote\][\s\S]*?\[/quote\])', descr, re.M,)
    for item in quoto:
        code = item.upper()
        if not any(i in code for i in judge_list):
            descr = descr.replace(item, '')
    hide_info = re.findall('(\[hide\][\s\S]*?\[/hide\])', descr, re.M,)
    for item in hide_info:
        descr = descr.replace(item, '')
    return descr


def format_descr_npupt(descr):
    tmp = []
    descr = descr.split('\n')
    for line in descr:
        if len(line.strip()) == 0:
            pass
        else:
            tmp.append(line)
    descr = '\n'.join(tmp)

    # 图片补链接
    descr = descr.replace(
        '[img]attachments',
        '[img]https://npupt.com/attachments')
    descr = descr.replace(
        '[img]torrents/image/',
        '[img]https://npupt.com/torrents/image/')

    return descr


def format_descr_tjupt(descr):
    tmp = []
    descr = descr.split('\n')
    for line in descr:
        if len(line.strip()) == 0:
            pass
        else:
            tmp.append(line)
    descr = '\n'.join(tmp)

    # 图片补链接
    descr = descr.replace(
        '[img]attachments',
        '[img]https://www.tjupt.org/attachments')
    descr = descr.replace(
        'https://www.tjupt.org/jump_external.php?ext_url=', '')
    descr = descr.replace('/jump_external.php?ext_url=', '')
    descr = descr.replace('%3A', ':')
    descr = descr.replace('%2F', '/')

    return descr


def format_descr_hdchina(descr):
    tmp = []
    descr = descr.split('\n')
    for line in descr:
        if len(line.strip()) == 0:
            pass
        else:
            tmp.append(line)
    descr = '\n'.join(tmp)

    descr = descr.replace('%3A', ':')
    descr = descr.replace('%2F', '/')
    descr = descr.replace('本资源仅限会员测试带宽之用，严禁用于商业用途！', '')
    descr = descr.replace('对用于商业用途所产生的法律责任，由使用者自负！', '')
    descr = descr.replace('[img]attachments/', '[img]https://hdchina.org/attachments/')
    return descr


def format_descr_mteam(descr):
    tmp = []
    descr = descr.split('\n')
    for line in descr:
        if len(line.strip()) == 0:
            pass
        else:
            tmp.append(line)
    descr = '\n'.join(tmp)

    img_url = re.findall('(\[img\][\s\S]*?\[/img\])', descr, re.S)
    for item in img_url:
        tmp = item
        while tmp.find('%') >= 0:
            tmp = unquote(tmp)
        descr = descr.replace(item, tmp)
    descr = descr.replace('imagecache.php?url=', '')

    return descr


# 根据构造的字典以及爬取到的类型相关字符串判断类型，字典待扩充
def get_type_from_info(info: str or list):
    if isinstance(info, list):
        info = ''.join(info)
    flag = False
    for item in type_dict.keys():
        if flag:
            break
        if info.find(item) >= 0:
            sub_info = type_dict[item]
            for sub_item in sub_info:
                if flag:
                    break
                for sub_item2 in sub_item[0]:
                    if info.find(sub_item2) >= 0:
                        code = sub_item[1]
                        flag = True
                        break

    if not flag:
        code = 409

    return code


# 接下来三个函数是三个html2bbcode的网站版实现，由于打包成exe,自带的不是很好用，不知道为啥
def to_bbcode_use_api(data_html):
    url = 'https://www.garyshood.com/htmltobb/'
    data = {
        'baseurl': '',
        'html': data_html.encode()
    }
    des_post = requests.post(url=url, data=data)

    return_html = des_post.content.decode()
    try:
        mysoup = BeautifulSoup(return_html, 'lxml')
        code = mysoup.find('textarea').get_text()
    except Exception:
        code = to_bbcode_use_api_2(data_html)

    return code


def to_bbcode_use_api_2(data_html):
    url = 'http://skeena.net/htmltobb/index.pl'
    data = {
        'html': data_html.encode()
    }
    des_post = requests.post(url=url, data=data)

    return_html = des_post.content.decode()
    try:
        mysoup = BeautifulSoup(return_html, 'lxml')
        code = mysoup.find('textarea').get_text()
    except Exception as exc:
        # print(exc)
        code = to_bbcode_use_api_3(data_html)

    return code


def to_bbcode_use_api_3(data_html):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/74.0.3729.169 Safari/537.36",
        'Cookie': 'csrftoken=11pSdyiaWLoC54kGmeEeNrbpynMayd5NRzxz2kiV99Qc5zXFQMkwzPn7hMPpv7nU'
    }
    session = requests.session()
    session.headers = headers

    url = 'https://html2bbcode.ru/converter/'
    data = {
        'csrfmiddlewaretoken': 'QxD85IWlX2yiTWBwytXpuAszocEarpRhG5LPUuW6aq0STrev21DHgYEh7BHpoj9o',
        'html': data_html
    }
    des_post = session.post(url=url, data=data)
    return_html = des_post.content.decode()
    try:
        soup = BeautifulSoup(return_html, 'lxml')
        code = soup.find('textarea', id='bbcode').get_text()
    except Exception:
        code = to_bbcode(data_html)
    return code


# 为了将网页无关的引用直接废除，有mediainfo关键字的规范化——有待改进
def format_mediainfo(soup, descr, mode=1):
    if mode == 1:
        fieldset = descr.find_all('fieldset')
        for field in fieldset:
            code = field.get_text().upper()
            if not any(i in code for i in judge_list):
                field.decompose()
            else:
                try:
                    legend = field.find('legend')
                    legend.decompose()
                except Exception as exc:
                    print(exc)
                    pass
                if code.find('海报') >= 0 or code.find('◎译　　名　') >= 0 or code.find('◎主　　演　') >= 0 \
                        or code.find('[img]') >= 0:
                    pass
                else:
                    new_string_toinsert = soup.new_string("[quote=iNFO][font=Courier New]")
                    field.insert(0, new_string_toinsert)
                    new_string_toappend = soup.new_string("[/font][/quote]")
                    field.append(new_string_toappend)
    elif mode == 0:  # 馒头和北洋园,南洋的官方种子
        try:
            code_top = descr.find('div', class_='codetop')
            code_top.decompose()
        except Exception:
            pass
        fieldset = descr.find_all('fieldset')
        for field in fieldset:
            code = field.get_text().upper()
            if not any(i in code for i in judge_list):
                field.decompose()
            else:
                try:
                    legend = field.find('legend')
                    legend.decompose()
                except Exception:
                    pass
                new_string_toinsert = soup.new_string("[quote=iNFO][font=Courier New]")
                field.insert(0, new_string_toinsert)
                new_string_toappend = soup.new_string("[/font][/quote]")
                field.append(new_string_toappend)
        codemain = descr.find('div', class_='codemain')
        try:
            new_string_toinsert = soup.new_string("[quote=iNFO][font=Courier New]")
            codemain.insert(0, new_string_toinsert)
            new_string_toappend = soup.new_string("[/font][/quote]")
            codemain.append(new_string_toappend)
        except Exception:
            pass
    elif mode == 2:  # 蒲公英
        fieldset = descr.find_all('blockquote', class_='quote')
        for field in fieldset:
            code = field.get_text().upper()
            if not any(i in code for i in judge_list):
                field.decompose()
            else:
                try:
                    p = field.find('p')
                    b = field.find('b')
                    p.decompose()
                    b.decompose()
                except Exception:
                    pass
                new_string_toinsert = soup.new_string("[quote=iNFO][font=Courier New]")
                field.insert(0, new_string_toinsert)
                new_string_toappend = soup.new_string("[/font][/quote]")
                field.append(new_string_toappend)

    elif mode == 3:  # mode = 3 TTG
        tables = descr.find_all('table', class_='main')
        for table in tables:
            code = table.get_text().upper()
            if not any(i in code for i in judge_list):
                table.decompose()
            else:
                new_string_toinsert = soup.new_string("[quote=iNFO][font=Courier New]")
                table.insert(0, new_string_toinsert)
                new_string_toappend = soup.new_string("[/font][/quote]")
                table.append(new_string_toappend)

    descr = to_bbcode_use_api(str(descr))
    return descr


# 判断是否有mediainfo，无则根据视频自己生成
def judge_nfo_existed(descr):
    if any(i in descr.upper() for i in mediainfo_judge):
        nfo = 'true'
    else:
        nfo = ''
    return nfo

