# -*- coding: utf-8 -*-
"""中文 REPL 交互解释器"""
import os
import codeop

from .translator import PandaTranslator


class 中文REPL:
    """PandaCode 中文交互式解释器"""

    def __init__(self):
        self.翻译器 = PandaTranslator()
        self.环境 = {"__name__": "__main__", "__builtins__": __builtins__}
        self.缓冲 = []
        self.提示符 = "🐼 >>> "
        self.续行符 = "   ... "
        self.编译器 = codeop.CommandCompiler()
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
            源码 = "\n".join(self.缓冲)

            if self._块未完成(源码):
                continue
            self._执行缓冲()

    def _欢迎(self):
        print("=" * 50)
        print("  🐼 PandaCode 中文交互解释器 v1.0.1")
        print("=" * 50)
        print("  直接输入中文代码，回车即执行")
        print("  多行块：第一行以中文冒号（：）结尾")
        print("          后续行需要自己敲 4 个空格缩进")
        print("          空行结束块")
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

    def _块未完成(self, 源码: str) -> bool:
        """用 codeop 判断块是否写完（和 Python 官方 REPL 一致）"""
        try:
            py = self.翻译器.translate(源码)
        except Exception:
            return False
        try:
            结果 = self.编译器(py, "<PandaCode>", "single")
        except (SyntaxError, OverflowError, ValueError):
            return False
        return 结果 is None

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