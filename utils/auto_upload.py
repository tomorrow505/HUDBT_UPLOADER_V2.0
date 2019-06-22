# -*- coding: utf-8 -*-
# Author:Chengli


import tkinter as tk
from tkinter.ttk import Treeview
from tkinter import Scrollbar, Frame, StringVar, LEFT, RIGHT, Y, messagebox
import datetime
import webbrowser
from utils import commen_component
import threading
import time
from time import sleep
import autoseed_methods
import get_rss_info
import pickle


CONFIG_DL_PATH = './conf/config_dl.json'
USER_BAK_TASK_PATH = './conf/bak_task.pickle'


class AutoUploadPage(tk.Frame):  # 继承Frame类
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # 存储任务列表
        self.task_dict = {}
        self.task_list = []
        self.onduty_list = []

        self.qb = ''

        self.is_rss_mode = False
        self.t = 'Recorde_rss'
        self.refresh_t = 'Recorde_task_list'

        # 布局组件的定义
        self.var_link = StringVar()

        self.entry_link = tk.Entry(self, textvariable=self.var_link, width=58, borderwidth=3,font=('Helvetica', '12'))
        self.entry_link.bind('<Return>', self.enter_add)
        self.button_add = tk.Button(self, text='Add', font=('Helvetica', '12'), width=6, command=self.add_task_by_click)

        self.frame_m = Frame(self)
        self.scrollBar = Scrollbar(self.frame_m)
        self.tree = Treeview(self.frame_m, columns=('c1', 'c2', 'c3'), show="headings", yscrollcommand=self.scrollBar.set)

        self.btnDelete = tk.Button(self, text='删除任务', command=self.delete_task)
        self.btnRefresh = tk.Button(self, text='备份任务', command=self.bak_task)

        self.rsshandler = get_rss_info.RssLinkHandler()

        self.config_dl = self.controller.config_dl

        self.create_page()

    def create_page(self):

        # 添加种子部分
        # LEFT
        self.entry_link.place(x=30, y=30, width=600, height=30)
        self.var_link.set('请输入种子详情链接：')
        self.entry_link.bind('<FocusIn>', self.on_entry_click)
        self.entry_link.bind('<FocusOut>', self.on_focus_out)
        self.entry_link.config(fg='grey')

        self.button_add.place(x=640, y=28, width=80, height=30)

        # 管理种子部分
        self.frame_m.place(x=28, y=80, width=700, height=450)

        # 在Frame容器中创建滚动条
        self.scrollBar.pack(side=RIGHT, fill=Y)

        # 在Frame容器中使用Treeview组件实现表格功能
        # Treeview组件，三列，显示表头，带垂直滚动条

        # 设置每列宽度和对齐方式
        self.tree.column('c1', width=400, anchor='w')
        self.tree.column('c2', width=140, anchor='center')
        self.tree.column('c3', width=120, anchor='center')

        # 设置每列表头标题文本
        self.tree.heading('c1', text='种子链接', command=lambda: self.treeview_sort_column(self.tree, 'c1', False))
        self.tree.heading('c2', text='添加时间', command=lambda: self.treeview_sort_column(self.tree, 'c2', False))
        self.tree.heading('c3', text='状态', command=lambda: self.treeview_sort_column(self.tree, 'c3', False))

        # 左对齐，纵向填充
        self.tree.pack(side=LEFT, fill=Y)
        self.tree.bind('<Double-1>', self.treeviewclick)

        # Treeview组件与垂直滚动条结合
        self.scrollBar.config(command=self.tree.yview)

        # 删除按钮
        self.btnDelete.place(x=160, y=550, width=120, height=30)

        # 刷新按钮
        self.btnRefresh.place(x=460, y=550, width=120, height=30)

    def on_entry_click(self, event):
        """function that gets called whenever entry is clicked"""
        if self.var_link.get() == '请输入种子详情链接：':
            self.var_link.set('')  # delete all the text in the entry
            self.entry_link.config(fg='black')

    def on_focus_out(self, event):
        if self.var_link.get() == '':
            self.var_link.set('请输入种子详情链接：')
            self.entry_link.config(fg='grey')

    # 添加下载任务
    def add_task_by_click(self):
        detail_link = self.var_link.get()
        self.add_task_by_link(detail_link)
        # 重置界面
        self.var_link.set('')
        self.entry_link.config(fg='grey')

    def all_time_refresh(self):
        while True:
            if len(self.onduty_list) == 0:
                break
            else:
                time.sleep(2)
                self.refresh_task()

    def enter_add(self, event):
        self.add_task_by_click()

    # 删除选中项的按钮
    def delete_task(self):
        if not self.tree.selection():
            tk.messagebox.showerror('抱歉', '你还没有选择，不能删除')
            return
        for item in self.tree.selection():
            detail_link = self.tree.item(item, 'values')[0]
            statu = self.tree.item(item, 'values')[2]
            if statu not in ['发布成功', '任务丢失']:
                chosen_task = self.task_dict[detail_link]

                hash_info = chosen_task.get_hash_info()
                if chosen_task.get_statu() != '发布成功' and hash_info:
                    self.qb.delete_permanently(hash_info)
                try:
                    commen_component.stop_thread(chosen_task)
                except ValueError:
                    pass
                except SystemError:
                    pass
                self.task_dict.pop(detail_link)
            self.task_list.remove(detail_link)

            if len(self.onduty_list) == 0:
                try:
                    commen_component.stop_thread(self.refresh_t)
                except ValueError:
                    pass
                except SystemError:
                    pass

            if detail_link in self.onduty_list:
                self.onduty_list.remove(detail_link)
            self.tree.delete(item)

    # 更新所有种子的下载状态
    def refresh_task(self):
        task_all = self.tree.get_children()
        for item in task_all:
            value_link = self.tree.item(item, 'values')[0]
            value_addtime = self.tree.item(item, 'values')[1]
            value_statu = self.tree.item(item, 'values')[2]
            if value_link in self.task_dict.keys():
                value_statu_now = self.task_dict[value_link].get_statu()
                if not value_statu == value_statu_now:
                    self.tree.item(item, values=(value_link, value_addtime, value_statu_now))
                    if value_statu_now == '发布成功' or value_statu_now == '任务丢失':
                        try:
                            commen_component.stop_thread(self.task_dict[value_link])
                        except ValueError:
                            pass
                        except SystemError:
                            pass
                        self.onduty_list.remove(value_link)
                        self.task_dict.pop(value_link)
                        if len(self.onduty_list) == 0:
                            try:
                                commen_component.stop_thread(self.refresh_t)
                            except ValueError:
                                pass
                            except SystemError:
                                pass

    def treeviewclick(self, event):
        selected_item = self.tree.selection()[0]
        link = self.tree.item(selected_item, 'values')[0]
        webbrowser.open(link)

    def treeview_sort_column(self, tv, col, reverse):  # Treeview、列名、排列方式
        ll = [(tv.set(k, col), k) for k in tv.get_children('')]
        ll.sort(reverse=reverse)  # 排序方式
        for index, (val, k) in enumerate(ll):  # 根据排序后索引移动
            tv.move(k, '', index)
        tv.heading(col, command=lambda: self.treeview_sort_column(
            tv, col, not reverse))  # 重写标题，使之成为再点倒序的标题

    def add_rss_task(self):
        while True:
            self.rsshandler.change_refresh_time(self.config_dl['refresh_time'])
            entries_list = self.rsshandler.get_entries(self.config_dl['Max_Size'])
            for item in entries_list:
                detail_link = item['link']
                if detail_link in self.task_list:
                    continue
                add_time = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                values = [detail_link, add_time, '准备下载']
                self.tree.insert('', 'end', values=values)
                new_task = autoseed_methods.AutoSeed(self.qb, item, self.config_dl)
                new_task.start()
                self.task_dict[detail_link] = new_task
                self.task_list.append(detail_link)
                self.onduty_list.append(detail_link)
                if len(self.onduty_list) == 1:
                    self.refresh_t = threading.Thread(target=self.all_time_refresh, args=())
                    self.refresh_t.start()
            if int(self.config_dl['refresh_time']) == 0:
                sleep(600)
            else:
                sleep(int(self.config_dl['refresh_time'])*60)

    def reopen_rss(self):
        try:
            commen_component.stop_thread(self.t)
        except ValueError:
            pass
        except SystemError:
            pass
        self.t = threading.Thread(target=self.add_rss_task, args=())
        self.t.start()
        self.is_rss_mode = True
        tk.messagebox.showinfo('提示', 'RSS模式已经重启')

    def init_qb(self):

        self.qb = self.controller.qb
        self.get_bak_task()
        self.check_rss_mode()

    def check_rss_mode(self):
        if self.config_dl['rss_open']:
            if not self.is_rss_mode:
                self.t = threading.Thread(target=self.add_rss_task, args=())
                self.t.start()
                self.is_rss_mode = True
                # tk.messagebox.showinfo('提示', 'RSS模式已经开启')
                return 'opened'
            else:
                return 'opened_already'
        else:
            if self.is_rss_mode:
                try:
                    commen_component.stop_thread(self.t)
                except ValueError:
                    pass
                except SystemError:
                    pass
                # tk.messagebox.showinfo('提示', 'RSS模式已经关闭')
                self.is_rss_mode = False
                return 'closed'
            else:
                return 'closed_already'

    def bak_task(self):
        self.refresh_task()
        bak_task = []  # 以列表的形式保存未完成的种子
        task_all = self.tree.get_children()
        for item in task_all:
            value_link = self.tree.item(item, 'values')[0]
            value_statu = self.tree.item(item, 'values')[2]
            if value_statu not in ['发布成功', '任务丢失']:
                task = self.task_dict[value_link]
                bak_task.append(task.get_origin_url())
                try:
                    commen_component.stop_thread(task)
                except ValueError:
                    pass
                except SystemError:
                    pass

        with open(USER_BAK_TASK_PATH, "wb") as bak_file:  # with open with语句可以自动关闭资源
            pickle.dump(bak_task, bak_file)

    def get_bak_task(self):
        try:
            with open(USER_BAK_TASK_PATH, "rb") as bak_file:
                bak_task = pickle.load(bak_file)
                if not bak_task:
                    return
                for item in bak_task:
                    if isinstance(item, dict):
                        link = item['link']
                    else:
                        link = item
                    add_time = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                    values = [link, add_time, '准备下载']
                    self.tree.insert('', 'end', values=values)
                    new_task = autoseed_methods.AutoSeed(self.qb, item, self.config_dl)
                    self.task_dict[link] = new_task
                    self.onduty_list.append(link)
                    self.task_list.append(link)
                    new_task.start()
                    if len(self.onduty_list) == 1:
                        self.refresh_t = threading.Thread(target=self.all_time_refresh, args=())
                        self.refresh_t.start()
        except FileNotFoundError:
            pass

    def add_task_by_link(self, string, *args):
        detail_link = string
        # 禁止空或者误操作
        if not detail_link or detail_link == '请输入种子详情链接：':
            return
        # 禁止重复添加的链接
        if detail_link in self.task_list:
            messagebox.showerror('错误', '重复添加的链接！')
            return
        # 禁止不支持的网站
        support_sign = commen_component.find_origin_site(detail_link)
        if support_sign == 0:
            messagebox.showerror('错误', '不支持的网站！')
            return

        torrent_id = commen_component.get_id(detail_link)
        if torrent_id == -1:
            messagebox.showerror('错误', '不是种子详情链接！')
            return
        # 显示任务到列表
        add_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').replace('-', '/')
        values = [detail_link, add_time, '准备下载']
        # 添加到尾部
        self.tree.insert('', 'end', values=values)
        # 添加到首部
        # self.tree.insert('', 0, values=values)

        # 添加任务到后台并开启
        # 构造元祖实现远程判断
        if args:
            detail_link_tuple = (args[0], detail_link)
        else:
            detail_link_tuple = detail_link
        new_task = autoseed_methods.AutoSeed(self.qb, detail_link_tuple, self.config_dl)
        new_task.start()
        self.task_dict[detail_link] = new_task
        self.task_list.append(detail_link)
        self.onduty_list.append(detail_link)
        if len(self.onduty_list) == 1:
            self.refresh_t = threading.Thread(target=self.all_time_refresh, args=())
            self.refresh_t.start()
        return '任务已经添加'

    def get_statu_by_link(self, link):
        task_all = self.tree.get_children()
        for item in task_all:
            value_link = self.tree.item(item, 'values')[0]
            if value_link == link:
                value_statu = self.tree.item(item, 'values')[2]
                return value_statu
        return 'no result'

    def cancle_task_by_link(self, detail_link):

        find = False
        task_all = self.tree.get_children()
        for item in task_all:
            link = self.tree.item(item, 'values')[0]
            if link == detail_link:
                self.tree.delete(item)
                find = True
                break
        if find:
            chosen_task = self.task_dict[detail_link]
            hash_info = chosen_task.get_hash_info()
            if chosen_task.get_statu() != '发布成功' and hash_info:
                self.qb.delete_permanently(hash_info)
            else:
                return '任务还未开始或已经完成'
            try:
                commen_component.stop_thread(chosen_task)
            except ValueError:
                return '未知错误'
            except SystemError:
                return '未知错误'
            self.task_list.remove(detail_link)
            self.task_dict.pop(detail_link)
            if detail_link in self.onduty_list:
                self.onduty_list.remove(detail_link)

            return '取消成功'
        else:
            return '没找到任务'

    def close_rss(self):
        self.config_dl['rss_open'] = False
        self.check_rss_mode()

