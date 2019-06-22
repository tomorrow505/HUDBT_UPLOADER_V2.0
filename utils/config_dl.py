# -*- coding: utf-8 -*-
# Author:Chengli


import tkinter as tk
from tkinter import Label, Entry, Button, StringVar, messagebox, LEFT
from tkinter.filedialog import askdirectory
import os
import json
from utils import commen_component

CONFIG_DL_PATH = './conf/config_dl.json'


class ConfigDlPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.config_dl = self.controller.config_dl

        self.label_1 = Label(self, text="**多个目录均衡硬盘容量，缓存用于存储少量临时文件**", fg='red', font=("Helvetica", 12))
        self.label_2 = Label(self, text="学习资源：", font=("Helvetica", 10))
        self.label_3 = Label(self, text="影视娱乐：", font=("Helvetica", 10))
        self.label_4 = Label(self, text="动画动漫：", font=("Helvetica", 10))
        self.label_5 = Label(self, text="其他资源：", font=("Helvetica", 10))
        self.label_6 = Label(self, text="缓存目录：", font=("Helvetica", 10))

        self.var_2 = StringVar()
        self.var_3 = StringVar()
        self.var_4 = StringVar()
        self.var_5 = StringVar()
        self.var_6 = StringVar()

        self.entry_2 = Entry(self, textvariable=self.var_2, width=70, borderwidth=3, font=('Helvetica', '14'))
        self.entry_3 = Entry(self, textvariable=self.var_3, width=70, borderwidth=3, font=('Helvetica', '14'))
        self.entry_4 = Entry(self, textvariable=self.var_4, width=70, borderwidth=3, font=('Helvetica', '14'))
        self.entry_5 = Entry(self, textvariable=self.var_5, width=70, borderwidth=3, font=('Helvetica', '14'))
        self.entry_6 = Entry(self, textvariable=self.var_6, width=70, borderwidth=3, font=('Helvetica', '14'))

        self.button_2 = Button(self, text="...", command=self.select_folder_study)
        self.button_3 = Button(self, text="...", command=self.select_folder_movie)
        self.button_4 = Button(self, text="...", command=self.select_folder_carton)
        self.button_5 = Button(self, text="...", command=self.select_folder_others)
        self.button_6 = Button(self, text="...", command=self.select_folder_cache)

        self.frame = tk.LabelFrame(self, text='更多配置', height=200, width=200)

        self.bool_check_rss = tk.IntVar()
        self.bool_check_anony = tk.IntVar()
        self.bool_check_server = tk.IntVar()

        self.check_rss = tk.Checkbutton(self.frame, text='是否开启RSS（默认关闭）', variable=self.bool_check_rss,
                                        command=self.check_rss, anchor=tk.W)
        self.check_anony = tk.Checkbutton(self.frame, text='是否关闭匿名（默认匿名）', variable=self.bool_check_anony,
                                          command=self.check_anony, anchor=tk.W)
        self.check_server = tk.Checkbutton(self.frame, text='是否开启服务器（默认关闭）', variable=self.bool_check_server,
                                           command=self.check_server, anchor=tk.W)

        self.var_port = tk.StringVar()
        self.label_port = tk.Label(self.frame, text='端口：', anchor=tk.W)
        self.ertry_port = tk.Entry(self.frame, textvariable=self.var_port)

        self.var_ip = tk.StringVar()
        self.label_ip = tk.Label(self.frame, text='主机地址：', anchor=tk.W)
        self.ertry_ip = tk.Entry(self.frame, textvariable=self.var_ip)

        self.var_refresh_time = tk.StringVar()
        self.label_refresh_time = tk.Label(self.frame, text='间隔：', anchor=tk.W)
        self.ertry_refresh_time = tk.Entry(self.frame, textvariable=self.var_refresh_time)

        self.button_submit = Button(self, text="确定", command=self.submit_configur_dl)
        self.button_reset = Button(self, text="重置", command=self.cancel)

        self.create_page()

    def create_page(self):
        self.label_1.pack(side="top", fill="x", pady=15)

        self.label_2.place(x=0, y=48, width=160, height=30)
        self.entry_2.place(x=125, y=48, width=520, height=30)
        self.button_2.place(x=660, y=46, width=20, height=30)

        self.label_3.place(x=0, y=88, width=160, height=30)
        self.entry_3.place(x=125, y=88, width=520, height=30)
        self.button_3.place(x=660, y=86, width=20, height=30)

        self.label_4.place(x=0, y=128, width=160, height=30)
        self.entry_4.place(x=125, y=128, width=520, height=30)
        self.button_4.place(x=660, y=126, width=20, height=30)

        self.label_5.place(x=0, y=168, width=160, height=30)
        self.entry_5.place(x=125, y=168, width=520, height=30)
        self.button_5.place(x=660, y=166, width=20, height=30)

        self.label_6.place(x=0, y=208, width=160, height=30)
        self.entry_6.place(x=125, y=208, width=520, height=30)
        self.button_6.place(x=660, y=206, width=20, height=30)

        self.button_submit.place(x=280, y=420, width=70, height=30)
        self.button_reset.place(x=420, y=420, width=70, height=30)

        self.frame.place(x=50, y=266, width=630, height=120)

        self.check_anony.place(x=40, y=55, width=180, height=30)
        self.check_rss.place(x=270, y=55, width=180, height=30)
        self.check_server.place(x=40, y=20, width=180, height=30)

        self.label_ip.place(x=270, y=20, width=60, height=30)
        self.ertry_ip.place(x=330, y=22, width=120, height=25)
        self.label_port.place(x=470, y=20, width=60, height=30)
        self.ertry_port.place(x=510, y=22, width=50, height=25)

        self.label_refresh_time.place(x=470, y=55, width=60, height=30)
        self.ertry_refresh_time.place(x=510, y=57, width=50, height=25)

        self.var_2.set(self.config_dl['study_path'])
        self.var_3.set(self.config_dl['movie_path'])
        self.var_4.set(self.config_dl['carton_path'])
        self.var_5.set(self.config_dl['others_path'])
        self.var_6.set(self.config_dl['cache_path'])

        self.var_ip.set(self.config_dl['server_ip'])
        self.var_port.set(self.config_dl['server_port'])
        self.var_refresh_time.set(self.config_dl['refresh_time'])

        self.bool_check_rss.set(self.config_dl['rss_open'])
        self.bool_check_server.set(self.config_dl['server_open'])
        self.bool_check_anony.set(self.config_dl['anony_close'])

        if not self.bool_check_server.get():
            self.ertry_port.config(state='readonly')
            self.ertry_ip.config(state='readonly')
        if not self.bool_check_rss.get():
            self.ertry_refresh_time.config(state='readonly')

    def select_folder_study(self):
        path_ = askdirectory()
        self.var_2.set(path_)

    def select_folder_movie(self):
        path_ = askdirectory()
        self.var_3.set(path_)

    def select_folder_carton(self):
        path_ = askdirectory()
        self.var_4.set(path_)

    def select_folder_others(self):
        path_ = askdirectory()
        self.var_5.set(path_)

    def select_folder_cache(self):
        path_ = askdirectory()
        self.var_6.set(path_)

    def submit_configur_dl(self):
        study_path = self.var_2.get()
        movie_path = self.var_3.get()
        carton_path = self.var_4.get()
        others_path = self.var_5.get()
        cache_path = self.var_6.get()

        img_path = cache_path + '/imgs'

        folder = os.path.exists(img_path)
        if not folder:
            os.makedirs(img_path)

        port = self.var_port.get()
        ip = self.var_ip.get()

        self.config_dl['study_path'] = study_path
        self.config_dl['movie_path'] = movie_path
        self.config_dl['carton_path'] = carton_path
        self.config_dl['others_path'] = others_path
        self.config_dl['img_path'] = img_path
        self.config_dl['cache_path'] = cache_path
        self.config_dl['rss_open'] = self.bool_check_rss.get()
        old_refresh_time =  self.config_dl['refresh_time']
        self.config_dl['refresh_time'] = self.var_refresh_time.get()
        self.config_dl['server_open'] = self.bool_check_server.get()
        self.config_dl['anony_close'] = self.bool_check_anony.get()
        self.config_dl['server_port'] = port
        self.config_dl['server_ip'] = ip

        with open(CONFIG_DL_PATH, 'w') as f:
            json.dump(self.config_dl, f)

        self.controller.config_dl = commen_component.load_config_dl()
        self.controller.frames['AutoUploadPage'].config_dl = commen_component.load_config_dl()
        self.controller.frames['HandUploadPage'].config_dl = commen_component.load_config_dl()
        self.controller.check_remote_server()
        result = self.controller.frames['AutoUploadPage'].check_rss_mode()

        if int(old_refresh_time) != int(self.config_dl['refresh_time']) and result == 'opened_already':
            self.controller.frames['AutoUploadPage'].reopen_rss()
        # messagebox.showinfo('提示', '配置完成！')

    def cancel(self):
        self.var_2.set('')
        self.var_3.set('')
        self.var_4.set('')
        self.var_5.set('')
        self.var_6.set('')
        if self.bool_check_anony.get() == 1:
            self.bool_check_anony.set(0)
        if self.bool_check_server.get() == 1:
            self.bool_check_server.set(0)
        if self.bool_check_rss.get() == 1:
            self.bool_check_rss.set(0)
        self.var_ip.set('')
        self.var_port.set('')
        self.ertry_port.config(state='readonly')
        self.ertry_ip.config(state='readonly')

    def check_rss(self):
        if not self.bool_check_rss.get():
            self.ertry_refresh_time.config(state='readonly')
        else:
            self.ertry_refresh_time.config(state='normal')

    def check_server(self):
        if not self.bool_check_server.get():
            self.ertry_port.config(state='readonly')
            self.ertry_ip.config(state='readonly')
        else:
            self.ertry_port.config(state='normal')
            self.ertry_ip.config(state='normal')

    def check_anony(self):
        if self.bool_check_anony:
            pass
        else:
            pass

