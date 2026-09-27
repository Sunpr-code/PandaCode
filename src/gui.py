# -*- coding: utf-8 -*-
"""PandaCode GUI 主窗口"""
import io
import os
import re
import sys
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from .theme import 颜色
from .editor import 带行号编辑器
from .runtime import PandaRuntime
from .translator import PandaTranslator


def 资源路径(名):
    """兼容源码运行和 PyInstaller 打包"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, 名)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", 名)


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
        try:
            self.root.iconbitmap(资源路径("panda.ico"))
        except Exception:
            pass
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
    # 启动函数
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