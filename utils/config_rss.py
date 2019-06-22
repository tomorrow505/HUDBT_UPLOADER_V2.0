# -*- coding: utf-8 -*-
# Author:Chengli


import tkinter as tk
import os
import pickle
from tkinter.ttk import Treeview
from tkinter import Scrollbar, Frame, StringVar, LEFT, RIGHT, Y, messagebox, Label, W


class RssPage(tk.Frame):  # 继承Frame类

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.rss_list = []

        self.rss_path = './conf/rss_config.pickle'

        if not os.path.isfile(self.rss_path):
            self.create_config()

        self.var_rss_link = StringVar()
        self.var_rss_site = StringVar()
        self.var_rss_name = StringVar()

        self.label_link = Label(self, text='链接：', anchor=W)
        self.label_name = Label(self, text='别名：', anchor=W)
        self.label_site = Label(self, text='站点：', anchor=W)

        self.entry_rss_link = tk.Entry(self, textvariable=self.var_rss_link, width=58, borderwidth=3,
                                       font=('Helvetica', '12'))
        self.entry_rss_name = tk.Entry(self, textvariable=self.var_rss_name, width=58, borderwidth=3,
                                       font=('Helvetica', '12'))
        self.entry_rss_site = tk.Entry(self, textvariable=self.var_rss_site, width=58, borderwidth=3,
                                       font=('Helvetica', '12'))
        self.button_add = tk.Button(self, text='添加',  width=6, command=self.add_to_list)

        self.frame_m = Frame(self)
        self.scrollBar = Scrollbar(self.frame_m)
        self.tree = Treeview(self.frame_m, columns=('c1', 'c2', 'c3'), show="headings",
                             yscrollcommand=self.scrollBar.set)

        self.button_delete = tk.Button(self, text='删除', command=self.delete_rss)
        self.button_save = tk.Button(self, text='保存', command=self.save_config)

        self.create_page()
        self.load_config()

    def load_config(self):
        try:
            with open(self.rss_path, "rb") as rss_file:
                rss_list = pickle.load(rss_file)
                for item in rss_list:
                    self.tree.insert('', 'end', values=[item[0], item[1], item[2]])
        except FileNotFoundError:
            pass

    def create_config(self):
        with open(self.rss_path, 'wb') as rss_file:
            self.rss_list = []
            pickle.dump(self.rss_list, rss_file)

    def save_config(self):
        rss_all = self.tree.get_children()
        self.rss_list.clear()
        for item in rss_all:
            value_rss_link = self.tree.item(item, 'values')[0]
            value_rss_name = self.tree.item(item, 'values')[1]
            value_rss_site = self.tree.item(item, 'values')[2]
            rss_tuple = (value_rss_link, value_rss_name, value_rss_site)
            self.rss_list.append(rss_tuple)

        with open(self.rss_path, 'wb') as rss_file:
            pickle.dump(self.rss_list, rss_file)

    def create_page(self):

        self.label_link.place(x=30, y=30, width=80, height=30)
        self.label_name.place(x=30, y=70, width=80, height=30)
        self.label_site.place(x=330, y=70, width=80, height=30)

        self.entry_rss_link.place(x=80, y=30, width=640, height=30)
        self.entry_rss_name.place(x=80, y=70, width=200, height=30)
        self.entry_rss_site.place(x=380, y=70, width=200, height=30)

        self.button_add.place(x=640, y=70, width=80, height=30)

        self.frame_m.place(x=55, y=120, width=680, height=420)

        # 在Frame容器中创建滚动条
        self.scrollBar.pack(side=RIGHT, fill=Y)

        # 在Frame容器中使用Treeview组件实现表格功能
        # Treeview组件，三列，显示表头，带垂直滚动条

        # 设置每列宽度和对齐方式
        self.tree.column('c1', width=400, anchor='center')
        self.tree.column('c2', width=140, anchor='center')
        self.tree.column('c3', width=120, anchor='center')

        # 设置每列表头标题文本
        self.tree.heading('c1', text='链接', command=lambda: self.treeview_sort_column(self.tree, 'c1', False))
        self.tree.heading('c2', text='别名', command=lambda: self.treeview_sort_column(self.tree, 'c2', False))
        self.tree.heading('c3', text='站点名称', command=lambda: self.treeview_sort_column(self.tree, 'c3', False))

        # 左对齐，纵向填充
        self.tree.pack(side=LEFT, fill=Y)
        # self.tree.bind('<Double-1>', self.treeviewclick)

        # Treeview组件与垂直滚动条结合
        self.scrollBar.config(command=self.tree.yview)

        # 删除按钮
        self.button_delete.place(x=160, y=550, width=120, height=30)

        # 刷新按钮
        self.button_save.place(x=460, y=550, width=120, height=30)

    def treeview_sort_column(self, tv, col, reverse):  # Treeview、列名、排列方式
        ll = [(tv.set(k, col), k) for k in tv.get_children('')]
        ll.sort(reverse=reverse)  # 排序方式
        for index, (val, k) in enumerate(ll):  # 根据排序后索引移动
            tv.move(k, '', index)
        tv.heading(col, command=lambda: self.treeview_sort_column(
            tv, col, not reverse))  # 重写标题，使之成为再点倒序的标题

    def add_to_list(self):
        value_rss_site = self.var_rss_site.get()
        value_rss_name = self.var_rss_name.get()
        value_rss_link = self.var_rss_link.get()
        values = [value_rss_link, value_rss_name, value_rss_site]
        self.tree.insert('', 'end', values=values)
        self.var_rss_link.set('')
        self.var_rss_name.set('')
        self.var_rss_site.set('')

    def delete_rss(self):
        if not self.tree.selection():
            tk.messagebox.showerror('抱歉', '你还没有选择，不能删除')
            return
        for item in self.tree.selection():
            self.tree.delete(item)
