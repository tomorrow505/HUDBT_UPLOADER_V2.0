# -*- coding: utf-8 -*-
# Author:tomorrow505
from tkinter import StringVar, Label, E, Button
from qbittorrent import Client
import pickle
import tkinter as tk

'''
用于登录qbit，并且将用户信息保存
'''

USER_INFO_PATH = './conf/user_info.pickle'


class LoginPage(tk.Frame):  # 继承Frame类
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.var_ip = StringVar()
        self.var_port = StringVar()
        self.var_name = StringVar()
        self.var_pwd = StringVar()

        self.label_ip = Label(self, text='主机地址：', anchor=E)
        self.label_port = Label(self, text='端口：', anchor=E)
        self.label_name = Label(self, text='登录账户：', anchor=E)
        self.label_pwd = Label(self, text='登录密码：', anchor=E)

        self.entry_ip = tk.Entry(self, textvariable=self.var_ip, width=60, borderwidth=3, font=('Helvetica', '10'))
        self.entry_port = tk.Entry(self, textvariable=self.var_port, width=60, borderwidth=3,
                                   font=('Helvetica', '10'))
        self.entry_name = tk.Entry(self, textvariable=self.var_name, width=60, borderwidth=3,
                                   font=('Helvetica', '10'))
        self.entry_pwd = tk.Entry(self, textvariable=self.var_pwd, width=60, borderwidth=3,
                                  font=('Helvetica', '10'))
        self.entry_pwd['show'] = '*'

        self.button_login = Button(self, text="登录", command=self.user_login)

        self.create_page()

    def create_page(self):

        self.label_ip.place(x=190, y=160, width=80, height=30)
        self.label_port.place(x=380, y=160, width=80, height=30)
        self.label_name.place(x=190, y=220, width=80, height=30)
        self.label_pwd.place(x=190, y=280, width=80, height=30)

        self.entry_ip.place(x=270, y=160, width=120, height=30)
        self.entry_port.place(x=470, y=160, width=50, height=30)
        self.entry_name.place(x=270, y=220, width=250, height=30)
        self.entry_pwd.place(x=270, y=280, width=250, height=30)
        self.button_login.place(x=290, y=350, width=200, height=30)

        try:
            with open(USER_INFO_PATH, "rb") as usr_file:
                usrs_info = pickle.load(usr_file)
                self.var_ip.set(usrs_info['ip'])
                self.var_port.set(usrs_info['port'])
                self.var_name.set(usrs_info['name'])
                self.var_pwd.set(usrs_info['pwd'])
        except FileNotFoundError:
            pass

    def user_login(self):

        try:
            ip = self.var_ip.get()
            port = self.var_port.get()
            name = self.var_name.get()
            pwd = self.var_pwd.get()
            qb = Client('http://{ip}:{port}/'.format(ip=ip, port=port))
            qb.login(name, pwd)

            # 测试是否通过
            qb.torrents()

            self.controller.qb = qb
            self.controller.login_statu = True

            with open(USER_INFO_PATH, "wb") as usr_file:  # with open with语句可以自动关闭资源
                usrs_info = {"ip": ip, 'port': port, 'name': name, 'pwd': pwd}  # 以字典的形式保存账户和密码
                pickle.dump(usrs_info, usr_file)

        except Exception as exc:
            tk.messagebox.showerror('Error', '登录失败：%s' % exc)
