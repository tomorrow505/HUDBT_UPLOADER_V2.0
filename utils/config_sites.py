# -*- coding: utf-8 -*-
# Author:Chengli


import tkinter as tk
from utils import commen_component
from selenium import webdriver
import json
import os
from tkinter import ttk, StringVar, Frame, Scrollbar, LEFT, RIGHT, Y, Entry, Label, Button
from time import sleep

USER_DATA_PATH = './conf/config_chrome.json'
CONFIG_SITE_PATH = './conf/config_sites.json'

hudbt = {
    'abbr': 'hudbt',
    'domain': 'https://hudbt.hust.edu.cn',
    'index': 'https://hudbt.hust.edu.cn/index.php',
    'passkey': '',
    'cookie': []
}
npupt = {
    'abbr': 'npupt',
    'domain': 'https://npupt.com',
    'index': 'https://npupt.com/index.php',
    'passkey': '',
    'cookie': []
}
stju = {
    'abbr': 'stju',
    'domain': 'https://pt.sjtu.edu.cn',
    'index': 'https://pt.sjtu.edu.cn/index.php',
    'passkey': '',
    'cookie': []
}
tjupt = {
    'abbr': 'tjupt',
    'domain': 'https://www.tjupt.org',
    'index': 'https://www.tjupt.org/index.php',
    'passkey': '',
    'cookie': []
}
byr = {
    'abbr': 'byr',
    'domain': 'https://bt.byr.cn',
    'index': 'https://bt.byr.cn/index.php',
    'passkey': '',
    'cookie': []
}
mteam = {
    'abbr': 'mteam',
    'domain': 'https://tp.m-team.cc',
    'index': 'https://tp.m-team.cc/index.php',
    'passkey': '',
    'cookie': []
}
ourbits = {
    'abbr': 'ourbits',
    'domain': 'https://ourbits.club',
    'index': 'https://ourbits.club/index.php',
    'passkey': '',
    'cookie': []
}
cmct = {
    'abbr': 'cmct',
    'domain': 'https://hdcmct.org',
    'index': 'https://hdcmct.org/index.php',
    'passkey': '',
    'cookie': []
}
hdchina = {
    'abbr': 'hdchina',
    'domain': 'https://hdchina.org',
    'index': 'https://hdchina.org/index.php',
    'passkey': '',
    'cookie': []
}
nypt = {
    'abbr': 'nypt',
    'domain': 'https://nanyangpt.com',
    'index': 'https://nanyangpt.com/index.php',
    'passkey': '',
    'cookie': []
}
ttg = {
    'abbr': 'ttg',
    'domain': 'https://totheglory.im',
    'index': 'https://totheglory.im/index.php',
    'passkey': '',
    'cookie': []
}
hdsky = {
    'abbr': 'hdsky',
    'domain': 'https://hdsky.me',
    'index': 'https://hdsky.me/index.php',
    'passkey': '',
    'cookie': []
}
frds = {
    'abbr': 'FRDS',
    'domain': 'https://pt.keepfrds.com',
    'index': 'https://pt.keepfrds.com/index.php',
    'passkey': '',
    'cookie': []
}
sites_dict = {
    "北邮人": byr, "蒲公英": npupt, "葡萄": stju, "北洋园": tjupt, "南洋": nypt, "M-team": mteam, "OurBits": ourbits, "CMCT": cmct,
    "瓷器": hdchina, "TTG": ttg, "天空": hdsky, "朋友": frds
}
back_site_dict = {
    "北邮人": byr, "蒲公英": npupt, "葡萄": stju, "北洋园": tjupt, "南洋": nypt, "M-team": mteam, "OurBits": ourbits, "CMCT": cmct,
    "瓷器": hdchina, "TTG": ttg, "天空": hdsky, "蝴蝶": hudbt, "朋友": frds
}


class ConfigSitesPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.var_user_data = StringVar()
        self.var_user_data.set('chrome用户数据路径：')
        self.entry_user_data = Entry(self, textvariable=self.var_user_data, width=58, borderwidth=3)
        self.button_2 = Button(self, text="保存配置", command=self.save_user_data)

        self.label = Label(self, text="当前可选的站点:", justify=LEFT)
        self.label_2 = Label(self, text="**提示：谷歌数据目录保存一次即可，当前仅TTG,HDSky需要passkey**", font=("Helvetica", 10), fg='red')
        self.comvalue = StringVar()  # 窗体自带的文本，新建一个值
        self.comboxlist = ttk.Combobox(self, font=("Helvetica", 10), textvariable=self.comvalue)  # 初始化

        self.comboxlist["values"] = tuple(['请选择']+list(sites_dict.keys()))
        self.comboxlist.current(0)
        # self.comboxlist.bind("<<ComboboxSelected>>", self.get_site)

        self.button = tk.Button(self, text="添加站点", command=self.add_site)

        self.var = StringVar()
        self.var.set('输入所选站点的passkey:')
        self.entry_1 = Entry(self, textvariable=self.var, width=58, borderwidth=3, )

        self.add_site = Frame(self)
        self.scrollBar = Scrollbar(self.add_site)
        self.tree = ttk.Treeview(self.add_site, columns=('c1', 'c2', 'c3'), show="headings",
                                 yscrollcommand=self.scrollBar.set)

        self.btnLoadCookie = tk.Button(self, text='加载本地COOKIE', command=self.load_cookie)
        self.btnDelete = tk.Button(self, text='删除', command=self.delete_chosen)
        self.btnGetCookie = tk.Button(self, text='获取COOKIE', command=self.get_cookie)

        self.create_page()

    def create_page(self):
        self.button_2.place(x=620, y=15, width=100, height=28)
        self.entry_user_data.place(x=20, y=15, width=580, height=28)
        self.entry_user_data.bind('<FocusIn>', self.user_data_click)
        self.entry_user_data.bind('<FocusOut>', self.user_data_out)
        self.entry_user_data.config(fg='grey')

        self.label.place(x=0, y=50, width=160, height=25)
        self.label_2.place(x=260, y=48, width=428, height=25)
        self.comboxlist.place(x=160, y=48, width=80, height=25)
        self.button.place(x=620, y=80, width=100, height=28)
        self.entry_1.place(x=20, y=80, width=580, height=28)
        self.entry_1.bind('<FocusIn>', self.passkey_click)
        self.entry_1.bind('<FocusOut>', self.passkey_out)
        self.entry_1.config(fg='grey')

        # 在Frame容器中创建滚动条
        self.scrollBar.pack(side=RIGHT, fill=Y)

        # 在Frame容器中使用Treeview组件实现表格功能
        # Treeview组件，三列，显示表头，带垂直滚动条

        # 设置每列宽度和对齐方式
        self.tree.column('c1', width=120, anchor='center')
        self.tree.column('c2', width=260, anchor='center')
        self.tree.column('c3', width=280, anchor='center')

        # 设置每列表头标题文本
        self.tree.heading('c1', text='站点名称', command=lambda: self.treeview_sort_column(self.tree, 'c1', False))
        self.tree.heading('c2', text='站点域名', command=lambda: self.treeview_sort_column(self.tree, 'c2', False))
        self.tree.heading('c3', text='passkey', command=lambda: self.treeview_sort_column(self.tree, 'c3', False))
        self.tree.insert('', 0, values=['蝴蝶', 'https://hudbt.hust.edu.cn', ''])

        # 左对齐，纵向填充
        self.tree.pack(side=LEFT, fill=Y)
        # self.tree.bind('<Double-1>', self.treeviewclick)

        # Treeview组件与垂直滚动条结合
        self.scrollBar.config(command=self.tree.yview)
        self.add_site.place(x=20, y=130, width=720, height=400)

        # 获取cookie按钮
        self.btnLoadCookie.place(x=60, y=550, width=120, height=30)
        # 删除按钮
        self.btnDelete.place(x=290, y=550, width=120, height=30)
        # 获取cookie按钮
        self.btnGetCookie.place(x=520, y=550, width=120, height=30)

    def add_site(self):
        if os.path.exists(USER_DATA_PATH):
            site_name = self.comboxlist.get()
            if not site_name == "请选择":
                site = sites_dict[site_name]
                site_domain = site['domain']
                passkey = self.var.get()
                if passkey == '输入所选站点的passkey:':
                    passkey = ''
                values = [site_name, site_domain, passkey]
                self.tree.insert('', 0, values=values)
                self.var.set('')
                sites_dict.pop(site_name)
                self.comboxlist["values"] = tuple(['请选择']+list(sites_dict.keys()))
                self.comboxlist.current(0)
            else:
                tk.messagebox.showinfo('错误', '请选择一个站点！')

    def treeview_sort_column(self, tv, col, reverse):  # Treeview、列名、排列方式
        ll = [(tv.set(k, col), k) for k in tv.get_children('')]
        ll.sort(reverse=reverse)  # 排序方式
        for index, (val, k) in enumerate(ll):  # 根据排序后索引移动
            tv.move(k, '', index)
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))  # 重写标题，使之成为再点倒序的标题

    def passkey_click(self, event):
        if self.var.get() == '输入所选站点的passkey:':
            self.var.set('')  # delete all the text in the entry
            self.entry_1.config(fg='black')

    def passkey_out(self, event):
        if self.var.get() == '':
            self.var.set('输入所选站点的passkey:')
            self.entry_1.config(fg='grey')

    def user_data_click(self, event):
        if self.var_user_data.get() == 'chrome用户数据路径：':
            self.var_user_data.set('')
            self.entry_user_data.config(fg='black')

    def user_data_out(self, event):
        if self.var_user_data.get() == '':
            self.var_user_data.set('chrome用户数据路径：')
            self.entry_user_data.config(fg='grey')

    # 获取cookies
    def get_cookie(self):
        if os.path.exists(USER_DATA_PATH):
            site_chosen = commen_component.load_pt_sites()
            try:
                with open(USER_DATA_PATH, 'r') as config_file:
                    user_data = json.load(config_file)['user_data']
                    user_data = '/'.join(user_data.split('\\'))
                    user_data = '--user-data-dir='+user_data
                    # print(user_data)
                    options = webdriver.ChromeOptions()
                    options.add_argument(user_data)
                    driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)

                    site_all = self.tree.get_children()
                    for site in site_all:
                        site_name = self.tree.item(site, 'values')[0]
                        passkey = self.tree.item(site, 'values')[2]
                        site_chosen[site_name] = back_site_dict[site_name]
                        site_chosen[site_name]['passkey'] = passkey
                        driver.get(site_chosen[site_name]['index'])
                        cookies_0 = driver.get_cookies()
                        cookies_1 = {}
                        for item in cookies_0:
                            cookies_1[item['name']] = item['value']
                        site_chosen[site_name]['cookie'] = cookies_1

                with open(CONFIG_SITE_PATH, 'w') as f:
                    json.dump(site_chosen, f)

                tk.messagebox.showinfo('提示', 'cookies加载成功')

                sleep(5)
                driver.quit()
            except Exception as exc:
                tk.messagebox.showerror('错误', 'cookies加载错误%s' % exc)
                sleep(5)
                driver.quit()

        else:
            tk.messagebox.showerror('错误', '用户数据目录未配置。')

    # 删除选中项的按钮
    def delete_chosen(self):
        if not self.tree.selection():
            tk.messagebox.showerror('错误', '请选择要删除的站点！')
            return
        for item in self.tree.selection():
            if self.tree.item(item, 'values')[0] == '蝴蝶':
                tk.messagebox.showerror('抱歉', '蝴蝶站点不能删除！')
            else:
                site_name = self.tree.item(item, 'values')[0]
                self.tree.delete(item)
                sites_dict[site_name] = back_site_dict[site_name]
                self.comboxlist["values"] = tuple(['请选择']+list(sites_dict.keys()))
                self.comboxlist.current(0)

    # 保存谷歌浏览器用户数据目录
    def save_user_data(self):
        user_data = {'user_data': self.var_user_data.get()}
        with open(USER_DATA_PATH, 'w') as f:
            json.dump(user_data, f)
            tk.messagebox.showinfo('提示', '用户数据目录保存成功')
            # self.var_user_data.set('')

    def clear_data(self):
        site_all = self.tree.get_children()
        for item in site_all:
            self.tree.delete(item)

    def load_cookie(self):
        try:
            with open(USER_DATA_PATH, 'r') as config_file:
                user_data = json.load(config_file)['user_data']
                self.var_user_data.set(user_data)
            pt_sites = commen_component.load_pt_sites()
            for site in pt_sites.keys():
                if site != '蝴蝶':
                    domain = pt_sites[site]['domain']
                    passkey = pt_sites[site]['passkey']
                    values = [site, domain, passkey]
                    self.tree.insert('', 0, values=values)
                    sites_dict.pop(site)
                    self.comboxlist["values"] = tuple(['请选择']+list(sites_dict.keys()))
                    self.comboxlist.current(0)
        except Exception:
            pass





