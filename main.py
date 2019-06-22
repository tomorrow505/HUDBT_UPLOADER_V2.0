# -*- coding: utf-8 -*-
# Author:tomorrow

from utils import auto_upload, hand_upload, login, commen_component, config_dl, config_rss, config_sites
import tkinter as tk
import os
import threading
from time import sleep
import time
from tkinter import messagebox
from PIL import Image, ImageTk
import win32api
import win32con
import socketserver


X = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
Y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)


class MainPage(tk.Tk):

    auto_page = ''

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.author = commen_component.AUTHOR
        self.version = commen_component.VERSION
        self.thanks_list = commen_component.THANK_LIST

        self.qb = ''
        self.login_statu = False
        self.is_server_open = False
        self.t = 'recorder_server'

        self.geometry('%dx%d+%d+%d' % (750, 600, (X - 750) / 2, (Y - 650) / 2))  # 设置窗口大小
        self.resizable(False, False)
        self.title('HUDBT-UPLOADER-%s' % self.version)
        self.img_path = './docs/bitbug_favicon.ico'
        # print(self.img_path)
        self.iconbitmap('', self.img_path)
        self.frames = {}
        self.config_dl = commen_component.load_config_dl()
        self.create_page()

    def create_page(self):
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # 创建frame供切换
        for F in (config_sites.ConfigSitesPage, config_dl.ConfigDlPage, auto_upload.AutoUploadPage,
                  hand_upload.HandUploadPage, login.LoginPage, config_rss.RssPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            ''' 
            put all of the utils in the same location;
            the one on the top of the stacking order
            will be the one that is visible.
            '''
            frame.grid(row=0, column=0, sticky="nsew")

        # 设置主菜单
        menu = tk.Menu(self)

        # 发布模式子菜单
        submenu = tk.Menu(menu, tearoff=0)
        submenu.add_command(label='自动转载', command=self.show_auto_upload)
        submenu.add_command(label='手动发布', command=self.show_hand_upload)
        menu.add_cascade(label='发布模式', menu=submenu)

        # 配置子菜单
        submenu = tk.Menu(menu, tearoff=0)
        submenu.add_command(label='站点配置', command=self.show_config_sites)
        submenu.add_command(label='下载配置', command=self.show_config_dl)
        submenu.add_command(label='清除缓存', command=self.clear_cache)
        menu.add_cascade(label='配置选项', menu=submenu)

        # RSS子菜单
        submenu = tk.Menu(menu, tearoff=0)
        submenu.add_command(label='RSS管理', command=self.show_rss)
        menu.add_cascade(label='RSS选项', menu=submenu)

        # 帮助子菜单
        submenu = tk.Menu(menu, tearoff=0)
        submenu.add_command(label='关于', command=self.about)
        submenu.add_command(label='宣传', command=self.publicity)
        menu.add_cascade(label='帮助', menu=submenu)

        self.config(menu=menu)

        MainPage.auto_page = self.frames['AutoUploadPage']

        # self.check_remote_server()

        # 调试
        # self.show_frame("RssPage")
        # self.show_frame("HandUploadPage")
        # self.show_frame("AutoUploadPage")
        # self.show_frame("ConfigDlPage")
        # self.show_frame("ConfigSitesPage")
        # self.show_frame("LoginPage")

        # 起始界面
        self.show_frame("LoginPage")

        # 监测是否登录
        t1 = threading.Thread(target=self.check, args=())
        t1.start()

    # 检查远程服务是否开启
    def check_remote_server(self):
        if not self.is_server_open:
            if self.config_dl['server_open']:
                try:
                    ip = self.config_dl['server_ip']
                    port = self.config_dl['server_port']
                    self.t = threading.Thread(target=self.open_server, args=(ip, int(port)))
                    self.t.start()
                    self.is_server_open = True

                    # tk.messagebox.showinfo('提示', '服务器开启成功')
                except Exception as ecx:
                    tk.messagebox.showerror('错误', '服务器模式开启失败%s ' % ecx)
        else:
            if not self.config_dl['server_open']:
                try:
                    commen_component.stop_thread(self.t)
                except ValueError:
                    pass
                except SystemError:
                    pass
                # tk.messagebox.showinfo('提示', '服务器模式已经关闭')
                self.is_server_open = False

    # 检查是否登录
    def check(self):
        while True:
            sleep(1)
            if self.login_statu:
                self.show_auto_upload()
                self.check_remote_server()
                self.frames['AutoUploadPage'].init_qb()
                self.delete_torrents_over_time()
                break

    def show_frame(self, page_name):
        '''
        Show a frame for the given page name
        '''
        frame = self.frames[page_name]
        frame.tkraise()

    def show_auto_upload(self):
        if self.login_statu:
            self.show_frame('AutoUploadPage')

    def show_hand_upload(self):
        if self.login_statu:
            self.show_frame('HandUploadPage')

    def show_config_sites(self):
        if self.login_statu:
            self.show_frame('ConfigSitesPage')

    def show_config_dl(self):
        if self.login_statu:
            self.show_frame('ConfigDlPage')

    def show_rss(self):
        if self.login_statu:
            self.show_frame('RssPage')

    # 关闭前call_back会执行这个函数
    def call_back(self):
        self.frames['AutoUploadPage'].bak_task()
        self.config_dl['server_open'] = False
        self.check_remote_server()
        self.frames['AutoUploadPage'].close_rss()
        try:
            commen_component.stop_thread(self.frames['AutoUploadPage'].refresh_t)
        except ValueError:
            pass
        except SystemError:
            pass
        except Exception:
            pass
        self.destroy()

    def open_server(self, ip, port):
        # 创建一个多线程TCP服务器
        server = socketserver.ThreadingTCPServer((ip, port), self.MyServer)
        # print("启动socketserver服务器！")
        # 启动服务器，服务器将一直保持运行状态
        server.serve_forever()

    # 清楚缓存文件
    def clear_cache(self):
        if not os.path.exists(self.config_dl['cache_path']):
            tk.messagebox.showerror('错误', '尚未配置缓存文件目录！！')
            return
        try:
            for pathdir in [self.config_dl['img_path'], self.config_dl['cache_path']]:
                os.chdir(pathdir)
                filelist = list(os.listdir())
                for file in filelist:
                    if os.path.isfile(file):
                        os.remove(file)
        except Exception as exc:
            tk.messagebox.showerror('失败', exc)

    # 创建内部类用于开启服务器
    class MyServer(socketserver.BaseRequestHandler):
        """
        必须继承socketserver.BaseRequestHandler类
        """

        def handle(self):
            """
            必须实现这个方法！
            :return:
            """
            conn = self.request  # request里封装了所有请求的数据
            conn.sendall('欢迎使用蝴蝶种鸡服务器！'.encode())
            while True:
                data = conn.recv(1024).decode().strip()
                if data == "exit":
                    # print("断开与%s的连接！" % (self.client_address,))
                    break
                elif data == 'help':
                    result = commen_component.show_info()
                else:
                    try:
                        data_ = data.split(' ')
                        if len(data_) > 2 or len(data_) < 2:
                            result = '参数提示：\n%s' % commen_component.show_info()
                        else:
                            method = data_[0]
                            detail_link = data_[1]
                            support_sign = commen_component.find_origin_site(detail_link)
                            if support_sign == 0:
                                result = '不支持的链接！！'
                            else:
                                torrent_id = commen_component.get_id(detail_link)
                                if torrent_id == -1:
                                    result = '不支持的链接！！'
                                else:
                                    if method == 'post':
                                        result = MainPage.auto_page.add_task_by_link(detail_link, 'remote')
                                    elif method == 'get':
                                        result = MainPage.auto_page.get_statu_by_link(detail_link)
                                    elif method == 'cancle':
                                        result = MainPage.auto_page.cancle_task_by_link(detail_link)
                                    else:
                                        result = '参数提示：\n%s' % commen_component.show_info()
                    except IndexError:
                        result = '参数提示：\n%s' % commen_component.show_info()

                # print("来自%s的客户端向你发来信息：%s" % (self.client_address, data))
                conn.sendall(('客户端指令：%s\n服务器结果：%s' % (data, result)).encode())

    # 关于
    def about(self):
        if self.login_statu:
            messagebox.showinfo(title='About', message='Author：{author}\n鸣谢：{thanks}'.format(
                author=self.author, thanks=self.thanks_list))

    # 宣传弹窗
    def publicity(self):
        if self.login_statu:
            top1 = tk.Toplevel(self)
            xuanchuan = './docs/xuanchuan.png'
            image = Image.open(xuanchuan)
            img = ImageTk.PhotoImage(image)
            canvas1 = tk.Canvas(top1, width=image.width, height=image.height, bg='white')
            canvas1.create_image(0, 0, image=img, anchor="nw")
            canvas1.pack()
            label = tk.Label(top1, text='微信扫一扫吧@_@.', font=("Helvetica", 11))
            label.pack()
            top1.wm_geometry(
                '%dx%d+%d+%d' % (image.width, image.height + 30, (X - image.width) / 2, (Y - image.height - 30) / 2))
            top1.wm_attributes('-topmost', 1)
            top1.mainloop()

    # 打开软件是提示删除超过30天的种子
    def delete_torrents_over_time(self):
        hash_list = []
        now = int(time.time())
        torrents = self.qb.torrents()
        for torrent in torrents:
            d = torrent['completion_on']
            if now - int(d) > 60*60*24*30 and torrent['tags'] != '保留':
                hash_list.append(torrent['hash'])
        if len(hash_list):
            result = tk.messagebox.askokcancel('提示', '是否删除超时的%d个种子?' % len(hash_list))
            if result:
                self.delete_permanently(hash_list)


if __name__ == "__main__":
    app = MainPage()
    app.protocol("WM_DELETE_WINDOW", app.call_back)
    app.mainloop()
    commen_component.kill_myself()
