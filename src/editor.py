# -*- coding: utf-8 -*-
"""带行号 + 语法高亮的编辑器控件"""
import re
import tkinter as tk
from tkinter import ttk

from .theme import 颜色
from .keywords import 流程关键字, 定义关键字, 逻辑关键字, 内置函数关键字, 全部关键字


class 带行号编辑器(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=颜色["背景"])
        self.行号栏 = tk.Canvas(self, width=50, bg=颜色["行号背景"],
                                highlightthickness=0, bd=0)
        self.行号栏.pack(side="left", fill="y")
        self.文本 = tk.Text(self, bg=颜色["背景"], fg=颜色["前景"],
                            insertbackground=颜色["前景"],
                            selectbackground=颜色["选中"],
                            font=("Consolas", 13), undo=True, wrap="none",
                            bd=0, highlightthickness=0, tabs=("1c",), **kwargs)
        self.文本.pack(side="left", fill="both", expand=True)
        self.滚动条 = ttk.Scrollbar(self, orient="vertical", command=self._滚动)
        self.滚动条.pack(side="right", fill="y")
        self.文本.configure(yscrollcommand=self.滚动条.set)
        self.文本.bind("<<Modified>>", self._内容变化)
        self.文本.bind("<KeyRelease>", self._刷新行号)
        self.文本.bind("<MouseWheel>", self._刷新行号)
        self.文本.bind("<Button-1>", self._刷新行号)
        self.文本.bind("<Configure>", self._刷新行号)
        self._配置标签()
        self.after(50, self._刷新行号)

    def _滚动(self, *args):
        self.文本.yview(*args)
        self._刷新行号()

    def _配置标签(self):
        t = self.文本
        t.tag_configure("流程关键字", foreground=颜色["关键字"], font=("Consolas", 13, "bold"))
        t.tag_configure("定义关键字", foreground=颜色["定义关键字"], font=("Consolas", 13, "bold"))
        t.tag_configure("逻辑关键字", foreground=颜色["关键字"])
        t.tag_configure("内置函数", foreground=颜色["内置函数"])
        t.tag_configure("字符串", foreground=颜色["字符串"])
        t.tag_configure("注释", foreground=颜色["注释"], font=("Consolas", 13, "italic"))
        t.tag_configure("数字", foreground=颜色["数字"])
        t.tag_configure("错误行", background="#5a1d1d")

    def _内容变化(self, event=None):
        if self.文本.edit_modified():
            self.高亮()
            self._刷新行号()
            self.文本.edit_modified(False)

    def _刷新行号(self, event=None):
        self.行号栏.delete("all")
        i = self.文本.index("@0,0")
        while True:
            信息 = self.文本.dlineinfo(i)
            if 信息 is None:
                break
            y = 信息[1]
            行号 = str(i).split(".")[0]
            self.行号栏.create_text(45, y, anchor="ne", text=行号,
                                    fill=颜色["行号前景"], font=("Consolas", 11))
            i = self.文本.index(f"{i}+1line")
            if self.文本.compare(i, ">=", "end"):
                break

    def 高亮(self):
        t = self.文本
        for tag in ("流程关键字", "定义关键字", "逻辑关键字", "内置函数",
                    "字符串", "注释", "数字"):
            t.tag_remove(tag, "1.0", "end")
        内容 = t.get("1.0", "end-1c")
        for 行号, 行文本 in enumerate(内容.split("\n"), start=1):
            self._高亮一行(行号, 行文本)

    def _高亮一行(self, 行号, 行文本):
        t = self.文本
        注释位置 = 行文本.find("#")
        代码部分 = 行文本 if 注释位置 < 0 else 行文本[:注释位置]
        if 注释位置 >= 0:
            t.tag_add("注释", f"{行号}.{注释位置}", f"{行号}.end")
        i = 0
        while i < len(代码部分):
            if 代码部分[i] in ("'", '"'):
                引号 = 代码部分[i]
                j = i + 1
                while j < len(代码部分):
                    if 代码部分[j] == "\\":
                        j += 2
                        continue
                    if 代码部分[j] == 引号:
                        j += 1
                        break
                    j += 1
                t.tag_add("字符串", f"{行号}.{i}", f"{行号}.{j}")
                i = j
            else:
                i += 1
        for m in re.finditer(r"\d+(?:\.\d+)?", 代码部分):
            t.tag_add("数字", f"{行号}.{m.start()}", f"{行号}.{m.end()}")
        for 词 in sorted(全部关键字, key=len, reverse=True):
            起点 = 0
            while True:
                idx = 代码部分.find(词, 起点)
                if idx < 0:
                    break
                前 = 代码部分[idx - 1] if idx > 0 else ""
                后i = idx + len(词)
                后 = 代码部分[后i] if 后i < len(代码部分) else ""

                def 是词字符(c):
                    return c.isalnum() or c == "_" or ("\u4e00" <= c <= "\u9fff")

                if not 是词字符(前) and not 是词字符(后):
                    已有 = t.tag_names(f"{行号}.{idx}")
                    if "字符串" not in 已有 and "注释" not in 已有:
                        if 词 in 流程关键字:
                            tag = "流程关键字"
                        elif 词 in 定义关键字:
                            tag = "定义关键字"
                        elif 词 in 逻辑关键字:
                            tag = "逻辑关键字"
                        else:
                            tag = "内置函数"
                        t.tag_add(tag, f"{行号}.{idx}", f"{行号}.{后i}")
                起点 = idx + len(词)

    def 标记错误行(self, 行号):
        self.文本.tag_add("错误行", f"{行号}.0", f"{行号}.end")

    def 清除错误标记(self):
        self.文本.tag_remove("错误行", "1.0", "end")

    def 获取内容(self):
        return self.文本.get("1.0", "end-1c")

    def 设置内容(self, 文本):
        self.文本.delete("1.0", "end")
        self.文本.insert("1.0", 文本)
        self.高亮()
        self._刷新行号()