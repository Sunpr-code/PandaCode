# -*- coding: utf-8 -*-
"""
🐼 PandaCode 中文编程器 - 单文件版（修正版）
============================================
直接运行：
    python pandacode.py            → 有图形环境进 GUI，没有则进中文 REPL
    python pandacode.py run x.pdc  → 命令行运行文件
    python pandacode.py -e "打印（'你好'）"
    python pandacode.py translate x.pdc
    python pandacode.py repl
"""
import io
import os
import re
import sys
import argparse
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk


# ============================================================
# 第一部分：关键字与符号映射
# ============================================================
KEYWORDS = {
    # ---------- 流程控制 ----------
    "如果": "if", "否则如果": "elif", "否则": "else",
    "当": "while", "对于": "for", "在": "in",
    "跳出": "break", "继续": "continue", "通过": "pass", "返回": "return",

    # ---------- 定义与导入 ----------
    "函数": "def", "类": "class", "导入": "import", "从": "from", "作为": "as",

    # ---------- 逻辑与常量 ----------
    "并且": "and", "或者": "or", "非": "not",
    "真": "True", "假": "False", "空": "None", "是": "is",

    # ---------- 异常处理 ----------
    "尝试": "try", "捕获": "except", "最终": "finally",
    "抛出": "raise", "断言": "assert",

    # ---------- 作用域 ----------
    "全局": "global", "非局部": "nonlocal", "删除": "del", "与": "with",

    # ---------- 异步与生成 ----------
    "异步": "async", "等待": "await", "生成": "yield", "匿名函数": "lambda",

    # ---------- 内置函数 ----------
    "打印": "print", "输入": "input", "长度": "len", "范围": "range",
    "类型": "type", "整数": "int", "浮点": "float", "字符串": "str",
    "列表": "list", "字典": "dict", "集合": "set", "元组": "tuple",
    "求和": "sum", "最大值": "max", "最小值": "min", "排序": "sorted",
    "枚举": "enumerate", "压缩": "zip", "映射": "map", "过滤": "filter",
    "绝对值": "abs", "四舍五入": "round", "打开": "open",

    # ---------- 面向对象（新增）----------
    "初始化": "__init__",
    "自己": "self",
    "父类": "super",

    # ---------- 异常类型（新增）----------
    "异常": "Exception",
    "值错误": "ValueError",
    "类型错误": "TypeError",
    "键错误": "KeyError",
    "索引错误": "IndexError",
    "文件未找到错误": "FileNotFoundError",
    "零除错误": "ZeroDivisionError",
}

OPERATORS = {
    "＋": "+", "－": "-", "＊": "*", "／": "/", "％": "%", "＝": "=",
    "＜": "<", "＞": ">", "！": "!", "＆": "&", "｜": "|", "＾": "^", "～": "~",
}

PUNCTUATION = {
    "：": ":", "；": ";", "，": ",", "（": "(", "）": ")",
    "【": "[", "】": "]", "｛": "{", "｝": "}",
    "“": '"', "”": '"', "‘": "'", "’": "'",
}


# ============================================================
# 第二部分：翻译器
# ============================================================
class PandaTranslator:
    def translate(self, source: str) -> str:
        return "\n".join(self._翻译行(line) for line in source.splitlines())

    def _翻译行(self, line: str) -> str:
        if not line.strip():
            return line

        缩进匹配 = re.match(r"^([ \t]*)", line)
        缩进 = 缩进匹配.group(1)
        内容 = line[len(缩进):]

        注释 = ""
        if "#" in 内容:
            i = 内容.index("#")
            注释 = 内容[i:]
            内容 = 内容[:i]

        内容, 字符串表 = self._保护字符串(内容)
        内容 = self._替换符号(内容)
        内容 = self._替换关键字(内容)
        内容 = self._还原字符串(内容, 字符串表)
        return 缩进 + 内容 + 注释

    def _保护字符串(self, text):
        串 = []

        def 替换(m):
            串.append(m.group(0))
            return f"__STR_{len(串) - 1}__"

        pattern = r'(["\'])(?:\\.|(?!\1).)*\1'
        return re.sub(pattern, 替换, text), 串

    def _还原字符串(self, text, 串):
        for i, s in enumerate(串):
            text = text.replace(f"__STR_{i}__", s)
        return text

    def _替换符号(self, text):
        for cn, en in {**OPERATORS, **PUNCTUATION}.items():
            text = text.replace(cn, en)
        return text

    def _替换关键字(self, text):
        for cn in sorted(KEYWORDS.keys(), key=len, reverse=True):
            en = KEYWORDS[cn]
            pattern = r"(?<![\w\u4e00-\u9fff])" + re.escape(cn) + r"(?![\w\u4e00-\u9fff])"
            text = re.sub(pattern, en, text)
        return text


# ============================================================
# 第三部分：运行时
# ============================================================
class PandaRuntime:
    def __init__(self, 环境=None):
        self.翻译器 = PandaTranslator()
        if 环境 is None:
            环境 = {
                "__name__": "__main__",
                "__builtins__": __builtins__,
            }
        self.环境 = 环境

    def translate(self, source):
        return self.翻译器.translate(source)

    def execute(self, source):
        py = self.翻译器.translate(source)
        code = compile(py, "<PandaCode>", "exec")
        exec(code, self.环境)


# ============================================================
# 第四部分：GUI 配色
# ============================================================
颜色 = {
    "背景": "#1e1e1e", "前景": "#d4d4d4",
    "关键字": "#569cd6", "内置函数": "#dcdcaa", "定义关键字": "#c586c0",
    "字符串": "#ce9178", "注释": "#6a9955", "数字": "#b5cea8",
    "行号背景": "#252526", "行号前景": "#858585", "选中": "#264f78",
    "输出背景": "#1e1e1e", "输出正常": "#d4d4d4",
    "输出错误": "#f48771", "输出成功": "#89d185",
}

流程关键字 = {"如果", "否则如果", "否则", "当", "对于", "在",
              "跳出", "继续", "通过", "返回"}
定义关键字 = {"函数", "类", "导入", "从", "作为", "尝试", "捕获", "最终",
              "抛出", "断言", "全局", "非局部", "删除", "与", "异步",
              "等待", "生成", "匿名函数", "初始化", "自己", "父类"}
逻辑关键字 = {"并且", "或者", "非", "真", "假", "空", "是",
              "异常", "值错误", "类型错误", "键错误", "索引错误",
              "文件未找到错误", "零除错误"}
内置函数关键字 = {"打印", "输入", "长度", "范围", "类型", "整数", "浮点",
                  "字符串", "列表", "字典", "集合", "元组", "求和", "最大值",
                  "最小值", "排序", "枚举", "压缩", "映射", "过滤", "绝对值",
                  "四舍五入", "打开"}
全部关键字 = 流程关键字 | 定义关键字 | 逻辑关键字 | 内置函数关键字


# ============================================================
# 第五部分：带行号编辑器
# ============================================================
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


# ============================================================
# 第六部分：主窗口
# ============================================================
class 熊猫编辑器:
    示例库 = {
        "hello": '''# 你好，世界！🐼
打印（"你好，世界！"）

甲 ＝ 10
乙 ＝ 20
打印（"甲 ＋ 乙 ＝", 甲 ＋ 乙）
''',
        "factorial": '''# 递归：阶乘
函数 阶乘（n）：
    如果 n ＜＝ 1：
        返回 1
    返回 n ＊ 阶乘（n － 1）

对于 i 在 范围（1, 8）：
    打印（i, "的阶乘是", 阶乘（i））
''',
        "loop": '''# 循环与条件
对于 数 在 范围（1, 11）：
    如果 数 ％ 2 ＝＝ 0：
        打印（数, "→ 偶数"）
    否则：
        打印（数, "→ 奇数"）

总和 ＝ 0
对于 i 在 范围（1, 101）：
    总和 ＝ 总和 ＋ i
打印（"1 到 100 的和 ＝", 总和）
''',
        "class": '''# 类与对象
类 熊猫：
    函数 初始化（自己, 名字, 年龄）：
        自己.名字 ＝ 名字
        自己.年龄 ＝ 年龄

    函数 说话（自己）：
        打印（"我是熊猫", 自己.名字, "，今年", 自己.年龄, "岁 🐼"）


圆圆 ＝ 熊猫（"圆圆", 3）
圆圆.说话（）
''',
        "try": '''# 异常处理
尝试：
    数 ＝ 整数（"abc"）
捕获 值错误 作为 错误：
    打印（"出错了：", 错误）
最终：
    打印（"无论如何都会执行"）
''',
    }

    def __init__(self, root):
        self.root = root
        self.root.title("🐼 PandaCode 中文编程器")
        self.root.geometry("1100x750")
        self.root.configure(bg=颜色["背景"])
        self.root.minsize(700, 500)
        self.运行时 = PandaRuntime()
        self.翻译器 = PandaTranslator()
        self.当前文件 = None
        self.已修改 = False
        self._居中()
        self._建菜单()
        self._建工具栏()
        self._建主体()
        self._建状态栏()
        self._绑快捷键()
        self._载入示例("hello")
        self.root.protocol("WM_DELETE_WINDOW", self._关闭窗口)

    def _居中(self):
        self.root.update_idletasks()
        w, h = 1100, 750
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _建菜单(self):
        菜单栏 = tk.Menu(self.root)
        文件 = tk.Menu(菜单栏, tearoff=0)
        文件.add_command(label="新建", accelerator="Ctrl+N", command=self.新建)
        文件.add_command(label="打开...", accelerator="Ctrl+O", command=self.打开)
        文件.add_command(label="保存", accelerator="Ctrl+S", command=self.保存)
        文件.add_command(label="另存为...", accelerator="Ctrl+Shift+S", command=self.另存为)
        文件.add_separator()
        文件.add_command(label="退出", command=self._关闭窗口)
        菜单栏.add_cascade(label="文件", menu=文件)

        运行 = tk.Menu(菜单栏, tearoff=0)
        运行.add_command(label="▶ 运行", accelerator="F5", command=self.运行)
        运行.add_command(label="🔍 查看翻译", accelerator="F6", command=self.查看翻译)
        运行.add_separator()
        运行.add_command(label="🧹 清空输出", command=self.清空输出)
        菜单栏.add_cascade(label="运行", menu=运行)

        示例 = tk.Menu(菜单栏, tearoff=0)
        for 名, 标题 in [("hello", "你好世界"), ("factorial", "阶乘递归"),
                         ("loop", "循环与条件"), ("class", "类与对象"),
                         ("try", "异常处理")]:
            示例.add_command(label=标题, command=lambda n=名: self._载入示例(n))
        菜单栏.add_cascade(label="示例", menu=示例)

        帮助 = tk.Menu(菜单栏, tearoff=0)
        帮助.add_command(label="关键字速查", command=self.显示关键字)
        帮助.add_command(label="关于", command=self.显示关于)
        菜单栏.add_cascade(label="帮助", menu=帮助)
        self.root.config(menu=菜单栏)

    def _建工具栏(self):
        栏 = tk.Frame(self.root, bg="#2d2d30", height=42)
        栏.pack(fill="x")

        def 按钮(text, cmd, bg="#3c3c3c"):
            b = tk.Button(栏, text=text, command=cmd, bg=bg, fg="white",
                          bd=0, padx=14, pady=6, font=("Microsoft YaHei", 10),
                          activebackground="#505050", activeforeground="white",
                          cursor="hand2")
            b.pack(side="left", padx=3, pady=6)

        按钮("▶ 运行 (F5)", self.运行, "#16825d")
        按钮("🔍 翻译 (F6)", self.查看翻译, "#0e639c")
        按钮("🧹 清空", self.清空输出)
        tk.Frame(栏, bg="#2d2d30", width=20).pack(side="left")
        按钮("💾 保存", self.保存)
        按钮("📁 打开", self.打开)
        self.文件名标签 = tk.Label(栏, text="未命名.pdc", bg="#2d2d30",
                                   fg="#cccccc", font=("Microsoft YaHei", 10))
        self.文件名标签.pack(side="right", padx=14)

    def _建主体(self):
        self.分栏 = tk.PanedWindow(self.root, orient="vertical", sashwidth=6,
                                   bg="#2d2d30", bd=0)
        self.分栏.pack(fill="both", expand=True)

        上框 = tk.Frame(self.分栏, bg=颜色["背景"])
        tk.Label(上框, text="  📝 中文代码区", anchor="w", bg="#2d2d30",
                 fg="#cccccc", font=("Microsoft YaHei", 10, "bold"),
                 pady=4).pack(fill="x")
        self.编辑器 = 带行号编辑器(上框)
        self.编辑器.pack(fill="both", expand=True)
        self.分栏.add(上框, height=430, stretch="always")

        下框 = tk.Frame(self.分栏, bg=颜色["背景"])
        输出头 = tk.Frame(下框, bg="#2d2d30")
        输出头.pack(fill="x")
        tk.Label(输出头, text="  📤 运行结果", anchor="w", bg="#2d2d30",
                 fg="#cccccc", font=("Microsoft YaHei", 10, "bold"),
                 pady=4).pack(side="left")
        self.状态点 = tk.Label(输出头, text="● 就绪", bg="#2d2d30",
                               fg="#858585", font=("Microsoft YaHei", 9))
        self.状态点.pack(side="right", padx=12)
        self.输出框 = scrolledtext.ScrolledText(下框, bg=颜色["输出背景"],
                                               fg=颜色["输出正常"],
                                               font=("Consolas", 12), bd=0,
                                               highlightthickness=0, wrap="word")
        self.输出框.pack(fill="both", expand=True)
        self.输出框.tag_configure("正常", foreground=颜色["输出正常"])
        self.输出框.tag_configure("错误", foreground=颜色["输出错误"])
        self.输出框.tag_configure("成功", foreground=颜色["输出成功"])
        self.输出框.tag_configure("提示", foreground="#569cd6")
        self.输出框.configure(state="disabled")
        self.分栏.add(下框, height=280, stretch="always")

    def _建状态栏(self):
        栏 = tk.Frame(self.root, bg="#007acc", height=24)
        栏.pack(fill="x", side="bottom")
        self.状态栏 = tk.Label(栏, text=" 🐼 就绪", bg="#007acc", fg="white",
                               anchor="w", font=("Microsoft YaHei", 9), padx=10)
        self.状态栏.pack(fill="x")

    def _绑快捷键(self):
        self.root.bind("<F5>", lambda e: self.运行())
        self.root.bind("<F6>", lambda e: self.查看翻译())
        self.root.bind("<Control-n>", lambda e: self.新建())
        self.root.bind("<Control-o>", lambda e: self.打开())
        self.root.bind("<Control-s>", lambda e: self.保存())
        self.root.bind("<Control-Shift-S>", lambda e: self.另存为())
        self.root.bind("<Control-l>", lambda e: self.清空输出())

    def 运行(self):
        self.清空输出()
        self.编辑器.清除错误标记()
        源码 = self.编辑器.获取内容()
        if not 源码.strip():
            self._输出("（代码为空）\n", "提示")
            return
        缓冲 = io.StringIO()
        旧out, 旧err = sys.stdout, sys.stderr
        sys.stdout = 缓冲
        sys.stderr = 缓冲
        出错 = False
        tb = ""
        try:
            self.运行时.execute(源码)
        except Exception as e:
            出错 = True
            tb = traceback.format_exc()
            缓冲.write(f"\n❌ 错误类型: {type(e).__name__}\n")
            缓冲.write(f"❌ 错误信息: {e}\n")
        finally:
            sys.stdout = 旧out
            sys.stderr = 旧err
        结果 = 缓冲.getvalue()
        if 结果:
            self._输出(结果, "错误" if 出错 else "正常")
        elif not 出错:
            self._输出("（程序运行完毕，无输出）\n", "提示")
        if 出错:
            匹配 = re.findall(r'File "<PandaCode>", line (\d+)', tb)
            if 匹配:
                行号 = int(匹配[-1])
                self.编辑器.标记错误行(行号)
                self._输出(f"\n📍 出错位置：第 {行号} 行\n", "错误")
            self.状态点.config(text="● 出错", fg=颜色["输出错误"])
            self.状态栏.config(text=" ❌ 运行出错")
        else:
            self.状态点.config(text="● 成功", fg=颜色["输出成功"])
            self.状态栏.config(text=" ✅ 运行成功")

    def 查看翻译(self):
        self.清空输出()
        源码 = self.编辑器.获取内容()
        try:
            py = self.翻译器.translate(源码)
            self._输出("=" * 50 + "\n翻译后的 Python 代码：\n" + "=" * 50 + "\n\n", "提示")
            self._输出(py + "\n", "正常")
            self.状态栏.config(text=" 🔍 翻译完成")
        except Exception as e:
            self._输出(f"❌ 翻译失败: {e}\n", "错误")

    def _输出(self, 文本, tag="正常"):
        self.输出框.configure(state="normal")
        self.输出框.insert("end", 文本, tag)
        self.输出框.see("end")
        self.输出框.configure(state="disabled")

    def 清空输出(self):
        self.输出框.configure(state="normal")
        self.输出框.delete("1.0", "end")
        self.输出框.configure(state="disabled")
        self.状态点.config(text="● 就绪", fg="#858585")

    def 新建(self):
        if not self._确认():
            return
        self.编辑器.设置内容("")
        self.当前文件 = None
        self.已修改 = False
        self._刷新标题()
        self.清空输出()

    def 打开(self):
        if not self._确认():
            return
        路径 = filedialog.askopenfilename(
            filetypes=[("PandaCode", "*.pdc"), ("Python", "*.py"), ("所有", "*.*")])
        if not 路径:
            return
        try:
            with open(路径, "r", encoding="utf-8") as f:
                self.编辑器.设置内容(f.read())
            self.当前文件 = 路径
            self.已修改 = False
            self._刷新标题()
            self.状态栏.config(text=f" 📂 已打开: {os.path.basename(路径)}")
        except Exception as e:
            messagebox.showerror("打开失败", str(e))

    def 保存(self):
        if self.当前文件 is None:
            return self.另存为()
        try:
            with open(self.当前文件, "w", encoding="utf-8") as f:
                f.write(self.编辑器.获取内容())
            self.已修改 = False
            self._刷新标题()
            self.状态栏.config(text=f" 💾 已保存: {os.path.basename(self.当前文件)}")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def 另存为(self):
        路径 = filedialog.asksaveasfilename(defaultextension=".pdc",
                                           filetypes=[("PandaCode", "*.pdc"), ("所有", "*.*")])
        if not 路径:
            return
        try:
            with open(路径, "w", encoding="utf-8") as f:
                f.write(self.编辑器.获取内容())
            self.当前文件 = 路径
            self.已修改 = False
            self._刷新标题()
            self.状态栏.config(text=f" 💾 已保存: {os.path.basename(路径)}")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def _确认(self):
        if not self.已修改:
            return True
        r = messagebox.askyesnocancel("未保存", "有未保存的修改，是否保存？")
        if r is None:
            return False
        if r:
            self.保存()
        return not self.已修改

    def _刷新标题(self):
        名 = os.path.basename(self.当前文件) if self.当前文件 else "未命名.pdc"
        self.文件名标签.config(text=名)
        self.root.title(f"🐼 PandaCode - {名}")

    def _载入示例(self, 名称="hello"):
        内容 = self.示例库.get(名称, self.示例库["hello"])
        self.编辑器.设置内容(内容)
        self.当前文件 = None
        self.已修改 = False
        self._刷新标题()
        self.状态栏.config(text=" 🐼 已载入示例，按 F5 运行")

    def 显示关键字(self):
        窗口 = tk.Toplevel(self.root)
        窗口.title("关键字速查")
        窗口.geometry("560x640")
        窗口.configure(bg=颜色["背景"])
        tk.Label(窗口, text="🐼 关键字速查表", bg=颜色["背景"],
                 fg="#569cd6", font=("Microsoft YaHei", 14, "bold"),
                 pady=10).pack()
        文本框 = scrolledtext.ScrolledText(窗口, bg="#252526", fg="#d4d4d4",
                                           font=("Consolas", 11), bd=0, wrap="word")
        文本框.pack(fill="both", expand=True, padx=10, pady=10)
        内容 = "【流程控制】\n"
        for 词, py in [("如果", "if"), ("否则如果", "elif"), ("否则", "else"),
                       ("当", "while"), ("对于", "for"), ("在", "in"),
                       ("跳出", "break"), ("继续", "continue"), ("返回", "return")]:
            内容 += f"  {词:<8} → {py}\n"
        内容 += "\n【定义与导入】\n"
        for 词, py in [("函数", "def"), ("类", "class"), ("导入", "import"),
                       ("从", "from"), ("作为", "as")]:
            内容 += f"  {词:<8} → {py}\n"
        内容 += "\n【面向对象】\n"
        for 词, py in [("初始化", "__init__"), ("自己", "self"), ("父类", "super")]:
            内容 += f"  {词:<8} → {py}\n"
        内容 += "\n【逻辑与常量】\n"
        for 词, py in [("并且", "and"), ("或者", "or"), ("非", "not"),
                       ("真", "True"), ("假", "False"), ("空", "None")]:
            内容 += f"  {词:<8} → {py}\n"
        内容 += "\n【异常处理】\n"
        for 词, py in [("尝试", "try"), ("捕获", "except"), ("最终", "finally"),
                       ("抛出", "raise"), ("异常", "Exception"),
                       ("值错误", "ValueError"), ("类型错误", "TypeError"),
                       ("键错误", "KeyError"), ("索引错误", "IndexError")]:
            内容 += f"  {词:<8} → {py}\n"
        内容 += "\n【内置函数】\n"
        for 词, py in [("打印", "print"), ("输入", "input"), ("长度", "len"),
                       ("范围", "range"), ("整数", "int"), ("字符串", "str"),
                       ("列表", "list"), ("字典", "dict")]:
            内容 += f"  {词:<8} → {py}\n"
        内容 += "\n【符号】\n"
        for 词, py in [("＋", "+"), ("－", "-"), ("＊", "*"), ("／", "/"),
                       ("＝", "="), ("＜", "<"), ("＞", ">"),
                       ("（", "("), ("）", ")"), ("：", ":"), ("，", ",")]:
            内容 += f"  {词:<8} → {py}\n"
        文本框.insert("1.0", 内容)
        文本框.configure(state="disabled")

    def 显示关于(self):
        messagebox.showinfo("关于",
                            "🐼 PandaCode v1.0.1（修正版）\n\n全中文编程语言\n\n"
                            "快捷键：F5 运行 / F6 翻译 / Ctrl+S 保存")

    def _关闭窗口(self):
        if self._确认():
            self.root.destroy()


# ============================================================
# 第七部分：中文 REPL 交互解释器
# ============================================================
class 中文REPL:
    """PandaCode 中文交互式解释器"""

    def __init__(self):
        self.翻译器 = PandaTranslator()
        self.环境 = {"__name__": "__main__", "__builtins__": __builtins__}
        self.缓冲 = []
        self.提示符 = "🐼 >>> "
        self.续行符 = "   ... "
        self.历史文件 = os.path.expanduser("~/.pandacode_history")
        self._加载历史()

    def _加载历史(self):
        try:
            import readline
            if os.path.exists(self.历史文件):
                readline.read_history_file(self.历史文件)
            readline.set_history_length(1000)
        except Exception:
            pass

    def _保存历史(self):
        try:
            import readline
            readline.write_history_file(self.历史文件)
        except Exception:
            pass

    def 启动(self):
        self._欢迎()

        while True:
            try:
                提示 = self.续行符 if self.缓冲 else self.提示符
                行 = input(提示)
            except (EOFError, KeyboardInterrupt):
                print()
                self._再见()
                break

            if not 行.strip():
                # 空行：如果缓冲里有未完成块，尝试执行
                if self.缓冲:
                    self._执行缓冲()
                continue

            if not self.缓冲:
                命令 = 行.strip()
                if 命令 in ("退出", "exit", "quit", "q"):
                    self._再见()
                    break
                if 命令 in ("帮助", "help", "?"):
                    self._帮助()
                    continue
                if 命令 in ("清空", "clear"):
                    os.system("clear" if os.name != "nt" else "cls")
                    self._欢迎()
                    continue
                if 命令 in ("环境", "vars"):
                    self._显示环境()
                    continue

            self.缓冲.append(行)

            # 如果本行以冒号结尾，说明块还没结束，继续读
            if self._是块开头(行):
                continue
            # 否则如果缓冲里最后一行还是冒号结尾（比如刚刚加了子行），继续
            if self._缓冲未结束():
                continue
            self._执行缓冲()

    def _欢迎(self):
        print("=" * 50)
        print("  🐼 PandaCode 中文交互解释器 v1.0.1")
        print("=" * 50)
        print("  直接输入中文代码，回车即执行")
        print("  支持多行块：以 如果/对于/函数/类/尝试 等开头")
        print("  ←→ 移动光标    ↑↓ 历史命令")
        print()
        print("  命令：帮助 / 清空 / 环境 / 退出")
        print("=" * 50)

    def _再见(self):
        self._保存历史()
        print("🐼 再见！欢迎再来写中文代码～")

    def _帮助(self):
        print("""
🐼 PandaCode 帮助
----------------------------------------
【输入代码】
  单行：直接敲，回车执行
    打印（"你好"）
    甲 ＝ 10
    甲 ＋ 乙

  多行块：第一行以中文冒号（：）结尾
    如果 甲 ＞ 5：
        打印（"大"）
    （空行结束块）

【内建命令】
  帮助 / help / ?    显示帮助
  清空 / clear       清屏
  环境 / vars        查看当前变量
  退出 / exit / q    退出
""")

    def _显示环境(self):
        可见 = {k: v for k, v in self.环境.items() if not k.startswith("__")}
        if not 可见:
            print("（暂无变量）")
            return
        for 名, 值 in 可见.items():
            print(f"  {名} = {repr(值)}")

    def _是块开头(self, 行: str) -> bool:
        """判断该行是否开启一个块（以冒号结尾）"""
        s = 行.strip()
        if not s:
            return False
        return s.endswith("：") or s.endswith(":")

    def _缓冲未结束(self) -> bool:
        """判断当前缓冲是否还没结束（最后一行以冒号结尾）"""
        if not self.缓冲:
            return False
        return self._是块开头(self.缓冲[-1])

    def _执行缓冲(self):
        源码 = "\n".join(self.缓冲)
        self.缓冲.clear()
        self._执行(源码)

    def _执行(self, 源码: str):
        try:
            py = self.翻译器.translate(源码)
        except Exception as e:
            print(f"❌ 翻译失败: {e}")
            return

        是表达式 = self._可能是表达式(源码)

        try:
            if 是表达式:
                try:
                    结果 = eval(compile(py, "<PandaCode>", "eval"), self.环境)
                    if 结果 is not None:
                        print(repr(结果))
                    return
                except SyntaxError:
                    pass

            code = compile(py, "<PandaCode>", "exec")
            exec(code, self.环境)
        except SyntaxError as e:
            print(f"❌ 语法错误: {e.msg}")
            print(f"   翻译后: {py}")
        except Exception as e:
            print(f"❌ {type(e).__name__}: {e}")

    def _可能是表达式(self, 源码: str) -> bool:
        s = 源码.strip()
        if not s or "\n" in s:
            return False
        语句开头 = ("如果", "否则", "当", "对于", "函数", "类",
                    "导入", "从", "尝试", "捕获", "最终", "返回",
                    "打印", "跳出", "继续", "抛出", "断言", "全局",
                    "非局部", "删除", "与", "异步", "等待", "生成",
                    "初始化")
        for kw in 语句开头:
            if s.startswith(kw):
                return False
        if "＝" in s or "=" in s:
            return False
        return True


# ============================================================
# 第八部分：命令行模式
# ============================================================
def 命令行(参数):
    parser = argparse.ArgumentParser(prog="pandacode",
                                     description="🐼 PandaCode 全中文编程语言")
    parser.add_argument("-v", "--version", action="store_true")
    parser.add_argument("-e", "--eval", help="直接执行代码")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("run", help="运行 .pdc 文件")
    p.add_argument("file")
    sub.add_parser("gui", help="启动图形界面")
    sub.add_parser("repl", help="启动中文交互解释器")
    t = sub.add_parser("translate", help="查看翻译")
    t.add_argument("file")

    args = parser.parse_args(参数)

    if args.version:
        print("PandaCode v1.0.1 🐼")
        return

    运行时 = PandaRuntime()

    if args.eval:
        运行时.execute(args.eval)
        return

    if args.command == "gui":
        启动图形()
        return

    if args.command == "repl":
        中文REPL().启动()
        return

    if args.command == "run":
        if not os.path.exists(args.file):
            print(f"❌ 找不到文件: {args.file}", file=sys.stderr)
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            运行时.execute(f.read())
    elif args.command == "translate":
        with open(args.file, "r", encoding="utf-8") as f:
            print(PandaTranslator().translate(f.read()))
    else:
        parser.print_help()


# ============================================================
# 第九部分：统一入口
# ============================================================
def 启动图形():
    root = tk.Tk()
    try:
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    熊猫编辑器(root)
    root.mainloop()


def 能启动图形() -> bool:
    """检测当前环境能否启动 Tkinter 图形界面"""
    if sys.platform in ("win32", "darwin"):
        try:
            r = tk.Tk()
            r.destroy()
            return True
        except Exception:
            return False

    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        return False

    try:
        r = tk.Tk()
        r.destroy()
        return True
    except Exception:
        return False


def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    参数 = [a for a in sys.argv[1:] if not a.startswith("--pyi-")]

    if 参数:
        命令行(参数)
        return

    if 能启动图形():
        if sys.platform == "win32":
            try:
                import ctypes
                hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                if hwnd:
                    ctypes.windll.user32.ShowWindow(hwnd, 0)
            except Exception:
                pass
        启动图形()
    else:
        中文REPL().启动()


if __name__ == "__main__":
    main()