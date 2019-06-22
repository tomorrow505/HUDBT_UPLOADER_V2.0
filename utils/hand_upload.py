# -*- coding: utf-8 -*-
# Author:Chengli


import shutil
import tkinter as tk
from tkinter import Label, StringVar, Button, ttk, W, E
import tkinter.filedialog
from tkinter.filedialog import askdirectory
import tkinter.scrolledtext
import re
import os
import commen_component
import get_douban_info
import get_media_info
import autoseed_methods
import html_handler

TITLE_FONT = ("Helvetica", 18, "bold")
type_dict = {
    "请选择": 0,
    "大陆电影": 401, "港台电影": 413, "亚洲电影": 414, "欧美电影": 415, "iPad": 430,
    "大陆剧集": 402, "港台剧集": 417, "亚洲剧集": 416, "欧美剧集": 418, "纪录片": 404,"体育": 407,
    "大陆综艺": 403, "港台综艺": 419, "亚洲综艺": 420, "欧美综艺": 421, "华语音乐":408, "日韩音乐": 422, "欧美音乐": 423,
    "古典音乐": 424, "原声音乐": 425, "音乐MV": 406, "其他": 409, "电子书": 432, "完结动漫": 405, "连载动漫": 427, "剧场OVA": 428,
    "动漫周边": 429, "游戏": 410, "游戏视频": 431, "软件": 411, "学习": 412, "MAC": 426, "HUST": 1037
}

extend_descr_before = """
   [quote][*][url=https://hudbt.hust.edu.cn/forums.php?action=viewtopic&forumid=10&topicid=23521][size=4][color=Magenta]☜新手入门必看☞蝴蝶-HUDBT精华帖汇总索引[/color][/size][/url]
   [*]自动上传的资源。一切以种子源文件为准，有误请举报或者联系管理员。
   [*]请大家积极保种，以便更多的人能够下载到资源。蝴蝶的发展离不开大家的努力，感谢您的支持！！！[/quote]   
   """

extend_descr_after = """

   [quote=感谢]Powered by HUDBT-UPLOADER-V1.1! 表示感谢！！
   [/quote]
"""


class HandUploadPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.qb = self.controller.qb
        self.raw_info = {
            'up_mode': 'HAND_MODE',
            'title': '',
            'small_descr': '',
            'descr': '',
            'descr_rss': '',
            'douban_info': '',
            'link': '',
            'recommand': '',
            'hash_info': '',
            'des_site': 'hudbt',
            'origin_site': '手动上传',
            'filename': '',
            'type_': 0,
            'uplver': '',
            'nfo': '',
            'torrent_path': '',
            'url': '',
            'detail_link': '无',
            'standard_sel': 0
        }

        self.config_dl = commen_component.load_config_dl()
        self.origin_torrent_path = ''
        self.video_path = ''
        self.total_info = ''

        self.var_torrent_name = StringVar()
        self.var_video_dir = StringVar()
        self.var_title = StringVar()
        self.var_subtitle = StringVar()
        self.var_douban_link = StringVar()

        self.label_torrent_name = Label(self, text='种子文件(*)：', anchor=E)
        self.label_torrent_name_show = Label(self, textvariable=self.var_torrent_name, anchor=W)
        self.var_torrent_name.set('未选择任何文件')

        self.label_video_name = Label(self, text='保存目录：', anchor=E)
        self.label_video_name_show = Label(self, textvariable=self.var_video_dir, anchor=W)
        self.var_video_dir.set('未选择任何目录')

        self.label_title = Label(self, text='主标题(*)：', anchor=E)
        self.label_subtitle = Label(self, text='副标题(*)：', anchor=E)
        self.label_douban_link = Label(self, text='豆瓣链接：', anchor=E)

        self.button_open_torrent = Button(self, text="选择文件", command=self.open_file)
        self.button_open_video_file = Button(self, text="选择目录", command=self.open_video_dir)

        self.button_get_descr = Button(self, text="一键获取简介", command=self.get_descr)

        self.entry_title = tk.Entry(self, textvariable=self.var_title, width=60, borderwidth=3, font=('Helvetica', '10'))
        self.entry_subtitle = tk.Entry(self, textvariable=self.var_subtitle, width=60, borderwidth=3, font=('Helvetica', '10'))
        self.entry_douban_link = tk.Entry(self, textvariable=self.var_douban_link, width=60, borderwidth=3,
                                          font=('Helvetica', '10'))

        self.txtContent = tkinter.scrolledtext.ScrolledText(self, height=23, font=("Helvetica", 10), wrap=tkinter.WORD)

        self.label_chose_type = Label(self, text='选择类型：')
        self.label_chose_hide_name = Label(self, text='是否匿名：')
        self.label_remand = Label(self, text='温馨提示：带*为必填项,豆瓣链接处也支持IMDB链接。\n主标题填英文名，不要带点，若不填将使用种子文件名。',
                                  fg='red', anchor=W)

        self.var_hide_name = tk.IntVar()
        self.checkbtn_hide_name = tk.Checkbutton(self, text="是", variable=self.var_hide_name)

        self.type_value = StringVar()  # 窗体自带的文本，新建一个值
        self.comboxlist = ttk.Combobox(self, textvariable=self.type_value)  # 初始化

        self.btnsubmit = tk.Button(self, text='提交发布', command=self.submit_task)
        self.btncancel = tk.Button(self, text='取消发布', command=self.cancel_task)

        self.create_page()

    def create_page(self):

        self.label_torrent_name.place(x=30, y=15, width=80, height=30)
        self.button_open_torrent.place(x=120, y=13, width=80, height=30)
        self.label_torrent_name_show.place(x=210, y=15, width=520, height=30)

        self.label_video_name.place(x=30, y=50, width=80, height=30)
        self.button_open_video_file.place(x=120, y=48, width=80, height=30)
        self.label_video_name_show.place(x=210, y=50, width=520, height=30)

        self.entry_title.place(x=120, y=85, width=520, height=30)
        self.label_title.place(x=30, y=85, width=80, height=30)
        self.entry_title.place(x=120, y=85, width=520, height=30)
        self.label_subtitle.place(x=30, y=120, width=80, height=30)
        self.entry_subtitle.place(x=120, y=120, width=520, height=30)
        self.label_douban_link.place(x=30, y=155, width=80, height=30)
        self.entry_douban_link.place(x=120, y=155, width=520, height=30)

        self.button_get_descr.place(x=30, y=200, width=120, height=30)

        self.label_remand.place(x=250, y=200, width=570, height=30)

        self.txtContent.place(x=42, y=250, width=680, height=280)

        self.label_chose_type.place(x=25, y=550, width=120, height=30)
        self.comboxlist["values"] = tuple(type_dict.keys())
        self.comboxlist.current(0)
        self.comboxlist.place(x=130, y=550, width=100, height=25)

        self.label_chose_hide_name.place(x=220, y=550, width=120, height=30)
        self.checkbtn_hide_name.place(x=310, y=550, width=30, height=30)

        # 提交按钮
        self.btnsubmit.place(x=450, y=550, width=100, height=30)
        # 取消按钮
        self.btncancel.place(x=600, y=550, width=100, height=30)

    def open_file(self):
        self.origin_torrent_path = tk.filedialog.askopenfilename(title='Open file', filetypes=[('Torrent files',
                                                                                                '*.torrent')])
        if self.origin_torrent_path:
            show_filename = self.origin_torrent_path.split('/')[-1]
            new_filename = re.sub('\.torrent', '', show_filename)
            new_filename = re.sub(r'^\[.{1,10}?\]|.mp4$|.mkv$|\[|\]|[\u4e00-\u9fff]|[^-\.@￡(A-Za-z0-9)]', '',
                                  new_filename)
            new_filename = ' '.join(new_filename.split('.')).strip()
            self.var_torrent_name.set(show_filename)
            self.var_title.set(new_filename)

    def backup_torrent(self):
        if self.origin_torrent_path:
            origin_torrent_name = self.origin_torrent_path.split('/')[-1]
            new_filename = re.sub('\.torrent', '', origin_torrent_name)
            new_filename = re.sub(r'^\[.{1,10}?\]|.mp4$|.mkv$|\[|\]|[\u4e00-\u9fff]|[^-\.@￡(A-Za-z0-9)]', '',
                                  new_filename)
            new_filename = ' '.join(new_filename.split('.')).strip()
            self.raw_info['filename'] = new_filename
            back_up_path = self.config_dl['cache_path']+'\\%s.torrent' % new_filename
            shutil.copyfile(self.origin_torrent_path, back_up_path)
            self.raw_info['torrent_path'] = back_up_path

    def open_video_dir(self):
        path_ = askdirectory()
        self.var_video_dir.set(path_)

    def get_descr(self):
        # 备份种子
        if not self.origin_torrent_path:
            tk.messagebox.showerror('错误', '请选择要上传的种子')
        else:
            self.backup_torrent()

            # 获取链接
            url = self.var_douban_link.get()
            douban_link = get_douban_info.get_douban_link(url)
            douban_info = ''
            if douban_link == '':
                tk.messagebox.showerror('错误', '非法的豆瓣/IMDB链接！')
            else:
                try:
                    douban_info = get_douban_info.get_douban_descr(douban_link)
                except Exception as exc:
                    tk.messagebox.showerror('错误', '获取豆瓣信息出错：%s' % exc)

            # 获取视频信息
            video_info = ''
            picture_info = ''
            if self.var_video_dir:
                self.raw_info['download_path'] = self.var_video_dir
                file_path = commen_component.parser_torrent(self.raw_info['torrent_path'])
                self.video_path = os.path.join(self.var_video_dir.get(), file_path)
                video_name = self.video_path.split('\\')[-1]
                try:
                    video_info = get_media_info.get_video_info(self.video_path)
                except Exception as exc:
                    tk.messagebox.showerror('错误', '获取视频信息出错：%s' % exc)
                try:
                    video_to_picture = re.sub('^\[.*?\]|[\u4e00-\u9fff]', '', video_name)
                    picture_path = self.config_dl['img_path'] + '/%s.jpg' % video_to_picture
                    picture_info = get_media_info.get_picture(self.video_path, picture_path)
                except Exception as exc:
                    tk.messagebox.showerror('错误', '获取截图信息出错：%s' % exc)

            try:
                imdb_link = re.search('.*imdb.com/title/(tt\d{5,9})', douban_info)
                imdb_link = 'https://www.imdb.com/title/' + imdb_link.group(1) + '/'
                self.raw_info['url'] = imdb_link
                recommand = html_handler.recommand_for_imdb(imdb_link)
            except Exception as exc:
                print(exc)
                recommand = ''
            self.raw_info['recommand'] = recommand
            self.total_info = douban_info + video_info + picture_info
            self.txtContent.insert(tkinter.INSERT, self.total_info)

    def get_title(self):
        self.raw_info['title'] = self.var_title.get()

    def get_type(self):
        type_ = self.comboxlist.get()
        if type_ == "请选择":
            tk.messagebox.showerror('错误', '请选择资源类型！')
        else:
            self.raw_info['type_'] = type_dict[type_]

    def get_subtitle(self):
        self.raw_info['small_descr'] = self.var_subtitle.get()

    def get_uplver(self):
        if self.var_hide_name.get() == 1:
            self.raw_info['uplver'] = 'yes'
        else:
            self.raw_info['uplver'] = 'no'

    def submit_task(self):
        self.raw_info['descr_rss'] = self.txtContent.get(0.0, tkinter.END)
        self.qb = self.controller.qb
        if not self.judge():
            tk.messagebox.showerror('错误', '信息不完整！')
            return 0
        self.get_title()
        self.get_subtitle()
        self.get_type()
        self.get_uplver()
        self.backup_torrent()  # 包含了get_filename

        tt = autoseed_methods.AutoSeed(self.qb, self.raw_info,  self.config_dl)
        tt.fak_upload()
        self.cancel_task()

    def cancel_task(self):
        if self.var_hide_name.get() == 1:
            self.var_hide_name.set(0)
        self.var_title.set('')
        self.var_subtitle.set('')
        self.var_douban_link.set('')
        self.var_torrent_name.set('未选择任何文件')
        self.var_video_dir.set('未选择任何目录')
        self.origin_torrent_path = ''
        self.raw_info = {
            'up_mode': 'HAND_MODE',
            'title': '',
            'small_descr': '',
            'descr': '',
            'descr_rss': '',
            'douban_info': '',
            'recommand': '',
            'hash_info': '',
            'des_site': 'hudbt',
            'origin_site': '手动上传',
            'filename': '',
            'type_': 0,
            'uplver': '',
            'nfo': '',
            'torrent_path': '',
            'url': '',
            'detail_link': '无',
            'standard_sel': 0
        }
        self.total_info = ''
        self.video_path = ''
        self.txtContent.delete(0.0, tkinter.END)
        self.comboxlist.current(0)

    def judge(self):
        if not self.origin_torrent_path:
            return 0
        else:
            return 1
