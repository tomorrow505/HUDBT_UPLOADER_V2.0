# -*- coding: utf-8 -*-
# Author:tomorrow505


from time import sleep
import re
import html_handler
import my_bencode
import requests
import os
from utils import commen_component
import get_media_info
import threading
import shutil
from urllib.parse import unquote

CONFIG_SITE_PATH = './conf/config_sites.json'

extend_descr_before = """
   [quote][*][url=https://hudbt.hust.edu.cn/forums.php?action=viewtopic&forumid=10&topicid=23521][size=4][color=Magenta]☜新手入门必看☞蝴蝶-HUDBT精华帖汇总索引[/color][/size][/url]
   [*]当前资源转自{site}，转载模式为：[color=Blue]{mode}[/color] 。一切信息以种子源文件为准，有误联系管理员。
   [*]转载阶段可能由于无监督转载，误转发他站禁转资源，如发现请及时举报。
   [*]部分种子长期保种，其余保种约[color=red][30][/color]天，断种恕不补种。
   [*]提倡发布员使用此种鸡，可以有效节约时间发布规范的种子，另：在此长期招募发布员。
   [*]期待你加入蝴蝶管理大家庭（假装有大家庭[em3][em3][em3]）[/quote]   
   """

extend_descr_after = """

   [quote=感谢]Powered by HUDBT-UPLOADER-{version}! 表示感谢！！
    来源：{detail_link}
   [/quote]
"""

reject_keywords = ['禁转', '禁止转载', '謝絕提取壓制轉載', '情色', '色情']


class AutoSeed (threading.Thread):

    pt_sites = commen_component.load_pt_sites()

    def __init__(self, qb, origin_url: str or dict or tuple, config_dl):
        super(AutoSeed, self).__init__()
        self.qb = qb

        self.raw_info = {
            'up_mode': 'HAND_MODE', 'detail_link': '', 'title': '', 'small_descr': '', 'descr': '', 'filename': '',
            'url': '', 'douban_info': '', 'type_': 0, 'uplver': 'yes', 'standard_sel': 0, 'origin_site': '',
            'recommand': '', 'nfo': '', 'hash_info': '', 'des_site': 'hudbt', 'descr_rss': '', 'picture_info': ''
        }

        if isinstance(origin_url, str):
            self.raw_info['detail_link'] = origin_url
            self.entrie = {}
        elif isinstance(origin_url, tuple):
            self.raw_info['detail_link'] = origin_url[1]
            self.raw_info['up_mode'] = 'REMOTE_MODE'
            self.entrie = {}
        else:
            self.raw_info['up_mode'] = 'RSS_MODE'
            self.entrie = origin_url
            self.raw_info['detail_link'] = self.entrie['link']

        self.torrent_id = commen_component.get_id(self.raw_info['detail_link'])
        self.statu = ['准备中…']
        self.config_dl = config_dl

        if self.config_dl['anony_close']:
            self.raw_info['uplver'] = 'no'

    def run(self):
        # 根据链接获取原始站点信息
        origin_site = commen_component.find_origin_site(self.raw_info['detail_link'])
        self.raw_info['origin_site'] = origin_site['abbr']

        # 无论哪种模式都先解析网页
        try:
            response = commen_component.get_response(self.raw_info['detail_link'], origin_site['cookie'])
            html = response.text
        except Exception as exc:
            return exc

        # 认怂，自动转载检查是不是禁转
        if any([html.find(item) >= 0 for item in reject_keywords]):
            if self.raw_info['up_mode'] == "RSS_MODE":
                self.statu.append("禁转？请检查")
                sleep(3)
                return

        # 开始解析网页，主要是为了获取类型然后分目录下载；获取hash_info判断下载情况
        try:
            self.statu.append('解析源网页……')
            htmlhandler = html_handler.HtmlHandler(self.raw_info['origin_site'], html)
            raw_info_tmp = htmlhandler.get_raw_info()
            for key in raw_info_tmp.keys():
                self.raw_info[key] = raw_info_tmp[key]
            # print('网页解析成功！')
        except Exception as exc:
            self.statu.append('网页解析出错')
            print('网页解析出错: %s' % exc)
            return exc
        #
        # return

        # 根据类型获取存文件储路径
        abs_file_dir = self.get_abs_file_dir(self.raw_info['type_'])

        # 获取种子下载路径并下载，返回种子存放路径，备份路径，以及下载信息
        download_url = commen_component.get_download_url(html, origin_site, self.torrent_id)
        self.statu.append("下载源种子")
        origin_torrent_path, dl_info = self.download_torrent(origin_site, self.torrent_id, download_url)
        if 'Error' in dl_info:
            self.statu.append('源种子下载失败')
            return

        # 根据备份种子获取下载的文件的相对路径以及hash值
        self.statu.append('解析源种子')
        try:
            file_path = commen_component.parser_torrent(origin_torrent_path)
            if not self.raw_info['hash_info']:
                self.raw_info['hash_info'] = my_bencode.get_hash(origin_torrent_path)
            # print(self.raw_info['hash_info'])
        except Exception as exc:
            self.statu.append('种子解析错误：%s' % exc)
            return
        if origin_site['abbr'] == 'mteam':
            my_bencode.change_tracker(origin_torrent_path)

        # 获取文件的绝对路径
        abs_file_path = os.path.join(abs_file_dir, file_path)

        # 根据下载的种子，下载文件到指定路径
        self.start_download(origin_torrent_path, abs_file_dir, 'false')
        self.statu.append('下载中…')

        if self.wait_for_download(self.raw_info['hash_info']):
            self.statu.append('下载成功')
        else:
            return

        # 下载成功后干事情
        if not self.raw_info['nfo']:
            try:
                video_info = get_media_info.get_video_info(abs_file_path)
            except Exception:
                video_info = ''
            self.raw_info['nfo'] = video_info
        else:
            if self.raw_info['nfo'] == 'true':
                self.raw_info['nfo'] = ''

        if not self.raw_info['descr_rss']:
            if self.raw_info['douban_info']:
                try:
                    video_name = abs_file_path.split('\\')[-1]
                    img_name = video_name + '.jpg'
                    img_name = re.sub('^\[.*?\]\.|[\u4e00-\u9fff]', '', img_name)
                    abs_img_path = self.config_dl['img_path'] + '/' + img_name
                    picture_info = get_media_info.get_picture(abs_file_path, abs_img_path)
                except Exception:
                    picture_info = ''
                self.raw_info['picture_info'] = picture_info

        self.statu.append('准备发布')
        log_info = self.upload_to_hudbt(self.raw_info, origin_torrent_path)

        if 'Succeed' in log_info:
            self.statu.append('发布成功')
        else:
            self.statu.append('发布失败')

    def get_origin_url(self):
        if self.entrie:
            return self.entrie
        else:
            return self.raw_info['detail_link']

    def get_statu(self):
        return self.statu[-1]

    def get_torrent_id(self):
        return commen_component.get_id(self.origin_url)

    def wait_for_download(self, hash_info):
        while True:
            try:
                torrent = self.qb.get_torrent(infohash=hash_info)
                if torrent['completion_date'] != -1:
                    return True
            except Exception:
                self.statu.append('任务丢失')
                return False
            sleep(5)

    def download_torrent(self, pt_site, tid, download_url):

        dl_info = []

        response = commen_component.get_response(download_url, pt_site['cookie'])
        # print(response.headers)
        content = response.headers['Content-Disposition']
        content = content.encode('ISO-8859-1').decode().replace('"', '')
        # print(content)
        if pt_site['domain'] == 'https://npupt.com' or pt_site['domain'] == 'https://totheglory.im':
            content = (unquote(content, 'utf-8'))
        try:
            origin_filename = re.search('filename=(.*?).torrent', content).group(1)
            # print(origin_filename)
        except AttributeError:
            # print('获取下载种子的文件名失败: %s' % exc)
            dl_info.append('Error')
            return '', dl_info

        # 处理种子名称
        filename = re.sub(r'^\[.{1,10}?\]|.mp4$|.mkv$|[\(\)]|\[|\]|[\u4e00-\u9fff]|[^-\.(A-Za-z0-9)]', ' ',
                          origin_filename)
        filename = ' '.join(filename.split('.'))
        filename = re.sub(' +', ' ', filename).lstrip()
        if pt_site['domain'] == 'https://pt.sjtu.edu.cn' or pt_site['domain'] == 'https://ourbits.club':
            filename = re.sub('^\d{3,10}', '', filename)
        else:
            pass

        self.raw_info['abbr'] = pt_site['abbr']
        if not filename:
            filename = '%s_%s' % (pt_site['abbr'], tid)

        self.raw_info['filename'] = filename
        origin_file_path = self.config_dl['cache_path'] + '\\%s.torrent' % filename

        # back_file_path = self.config_dl['cache_path'] + '\\%s_back.torrent' % filename

        try:
            response.raise_for_status()
            f = open(origin_file_path, 'wb')
            for chunk in response.iter_content(100000):
                f.write(chunk)
            f.close()
            # print('种子下载保存成功！')
            dl_info.append('Torrent Downloded')

        except Exception:
            # print('种子下载失败: %s' % exc)
            dl_info.append('Error')

        return origin_file_path, dl_info

    def get_abs_file_dir(self, type_):
        if type_ in [401, 413, 414, 415, 402, 417, 416, 418, 403, 419, 420, 421]:
            if type_ in [401, 413, 414, 415]:
                self.raw_info['category'] = '电影'
            elif type_ in [402, 417, 416, 418]:
                self.raw_info['category'] = '剧集'
            elif type_ in [403, 419, 420, 421]:
                self.raw_info['category'] = '综艺'
            abs_file_dir = self.config_dl['movie_path']
        elif type_ in [412]:
            abs_file_dir = self.config_dl['study_path']
            self.raw_info['category'] = '学习'
        elif type_ in [429, 427]:
            abs_file_dir = self.config_dl['carton_path']
            self.raw_info['category'] = '动漫'
        else:
            if type_ == 407:
                self.raw_info['category'] = '体育'
            elif type_ in [408, 422, 423, 424, 425]:
                self.raw_info['category'] = '音乐'
            else:
                self.raw_info['category'] = '其他'

            abs_file_dir = self.config_dl['others_path']

        return abs_file_dir

    def start_download(self, torrent_path, dl_path, flag):
        torrent_file = open(torrent_path, 'rb')
        self.qb.download_from_file(torrent_file, savepath=dl_path, category=self.raw_info['category'],
                                   skip_checking=flag)
        torrent_file.close()

    def upload_to_hudbt(self, raw_info, origin_torrent_path, params=None, files=None):

        log_info = []
        hudbt = AutoSeed.pt_sites['蝴蝶']

        des_url = "{host}/takeupload.php".format(host=hudbt['domain'])

        upload_torrent_path = self.backup_torrent(origin_torrent_path)
        os.remove(origin_torrent_path)
        torrent_file = open(upload_torrent_path, "rb")

        try:
            files = [("file", (raw_info['filename'], torrent_file, "application/x-bittorrent")),
                     ("nfo", ("", "", "application/octet-stream")), ]
        except Exception:
            log_info.append('Error')

            # sys.exit(0)

        if raw_info['title'] != '':
            name = raw_info['title']
        else:
            name = raw_info['filename']

        if name.lower().find('1080p') >= 0:
            raw_info['standard_sel'] = 1
        elif name.lower().find('720p') >= 0:
            raw_info['standard_sel'] = 3
        if name.upper().endswith(("PAD", 'IHD')):
            raw_info['type_'] = 430

        if raw_info['descr_rss']:
            raw_info['descr'] = raw_info['descr_rss'] + raw_info['recommand']
        else:
            if raw_info['douban_info']:
                raw_info['descr'] = raw_info['douban_info'] + raw_info['nfo'] + raw_info['picture_info']

        extend_descr_before_1 = extend_descr_before.format(site=raw_info['origin_site'], mode=raw_info['up_mode'])
        extend_descr_after_1 = extend_descr_after.format(detail_link=raw_info['detail_link'],
                                                         version=commen_component.VERSION)

        # # 置换图片地址
        # raw_info['descr'] = self.change_img_url(raw_info['descr'])

        raw_info['descr'] = extend_descr_before_1 + raw_info['descr'] + \
            raw_info['nfo'] + raw_info['recommand'] + extend_descr_after_1

        data = {
            "dl-url": "",
            "name": name.strip(),
            "small_descr": raw_info["small_descr"],
            "url": raw_info["url"],
            "descr": raw_info["descr"],
            "type": str(raw_info["type_"]),
            "data[Tcategory][Tcategory][]": "",
            "standard_sel": str(raw_info["standard_sel"]),
            "uplver": raw_info['uplver'],
        }

        des_post = requests.post(url=des_url, params=params, data=data, files=files, cookies=hudbt['cookie'])
        # content = des_post.content.decode()
        # print(content)
        seed_torrent_download_id = commen_component.get_id(des_post.url)
        if seed_torrent_download_id == -1:
            try:
                content = des_post.content.decode()
                seed_torrent_download_id = re.search('该种子已存在！.*id=(\d{2,8})', content)
                log_info.append('该种子已经上传，进入辅种程序。')
                # print(content)
                log_info.append('重复的种子')
                seed_torrent_download_id = seed_torrent_download_id.group(1)
            except Exception as exc:
                print('出错了！%s' % exc)
                seed_torrent_download_id = -1
        if seed_torrent_download_id == -1:
            log_info.append('Error')
            # sys.exit(0)
        else:
            # print('准备下载蝴蝶种子！ id = %s' % seed_torrent_download_id)
            download_url = "{host}/download.php?id={tid}".format(host=hudbt['domain'], tid=seed_torrent_download_id)
            origin_file_path, dl_info = self.download_torrent(hudbt, seed_torrent_download_id, download_url)
            if 'Error' in dl_info:
                log_info.append('重下载种子错误')
                log_info.append('Error')
            else:
                abs_file_dir = self.get_abs_file_dir(raw_info['type_'])
                if 'download_path' in raw_info.keys():
                    abs_file_dir = raw_info['download_path']
                    raw_info['category'] = self.raw_info['category']
                # else:
                #     abs_file_dir = self.get_abs_file_dir(raw_info['type_'])
                self.start_download(origin_file_path, abs_file_dir, 'true')
                log_info.append('Succeed')

            # txt_path = '%s_%s_%s.txt' % (raw_info['filename'], 'hudbt', seed_torrent_download_id)
            # txt_path = os.path.join(self.config_dl['cache_path'], txt_path)
            # with open(txt_path, 'w', encoding='utf-8') as f:
            #     f.write(raw_info['descr'].encode().decode())
            torrent_file.close()
            os.remove(upload_torrent_path)
            os.remove(origin_file_path)
        return log_info

    def get_hash_info(self):
        return self.raw_info['hash_info']

    def fak_upload(self):
        torrent_path = self.entrie['torrent_path']
        # print(torrent_path)
        log_info = self.upload_to_hudbt(self.entrie, torrent_path)
        return log_info

    def change_img_url(self, descr):
        if self.raw_info['douban_info']:
            try:
                douban_img_url = re.match('\[img\](.*)\[/img\]', self.raw_info['douban_info'])
                douban_img_url = douban_img_url.group(1)
            except AttributeError:
                douban_img_url = ''

            try:
                origin_img_url = re.match('\[img\](.*)\[/img\]', descr)
                origin_img_url = origin_img_url.group(1)
            except AttributeError:
                origin_img_url = ''

            if origin_img_url:
                descr = descr.replace(origin_img_url, douban_img_url)
            else:
                descr = '[img]%s[/img]\n%s' % (douban_img_url, descr)

        return descr

    # 修复发布失败的bug
    def backup_torrent(self, origin_torrent_path):

        origin_torrent_name = origin_torrent_path.split('\\')[-1]
        new_filename = re.sub('\.torrent', '', origin_torrent_name)
        new_filename = re.sub(r'^\[.{1,10}?\]|.mp4$|.mkv$|\[|\]|[\u4e00-\u9fff]|[^-\.@￡(A-Za-z0-9)]', '',
                              new_filename)
        new_filename = ' '.join(new_filename.split('.')).strip()
        back_up_path = self.config_dl['cache_path']+'\\%s_back.torrent' % new_filename
        shutil.copyfile(origin_torrent_path, back_up_path)

        return back_up_path
