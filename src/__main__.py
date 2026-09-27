# -*- coding: utf-8 -*-
"""
src/__main__.py
================
支持 `python -m src` 运行。

行为与根目录的 PandaCode.py 一致：
    python -m src                  → 自动（有图形进 GUI，无则进 REPL）
    python -m src run x.pdc        → 命令行运行
    python -m src -e "打印（'你好'）"
    python -m src repl
    python -m src gui
"""
import os
import sys

# 把项目根目录加入 sys.path，保证 `from src.xxx` 能找到
_根目录 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _根目录 not in sys.path:
    sys.path.insert(0, _根目录)

from src.repl import 中文REPL


def 能启动图形() -> bool:
    """检测当前环境能否启动 Tkinter 图形界面"""
    import tkinter as tk
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


def 有控制台() -> bool:
    """判断当前进程是否有可用的控制台"""
    if sys.stdout is None:
        return False
    try:
        sys.stdout.write("")
        sys.stdout.flush()
        return True
    except Exception:
        return False


def _弹窗(文本: str, 标题: str = "PandaCode"):
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, 文本, 标题, 0x40)
            return
        except Exception:
            pass
    try:
        from tkinter import messagebox as mb
        import tkinter as tk
        r = tk.Tk()
        r.withdraw()
        mb.showinfo(标题, 文本)
        r.destroy()
    except Exception:
        pass


def _隐藏控制台_尝试():
    if sys.platform != "win32":
        return
    try:
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass


def main():
    if sys.platform == "win32":
        try:
            if sys.stdout is not None:
                sys.stdout.reconfigure(encoding="utf-8")
            if sys.stderr is not None:
                sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    参数 = [a for a in sys.argv[1:] if not a.startswith("--pyi-")]

    # ---------- 有命令行参数 ----------
    if 参数:
        if not 有控制台():
            _弹窗(
                "当前是 GUI 版本，无法在命令行输出。\n\n"
                "请使用带控制台的 PandaCode-CLI.exe，\n"
                "或直接双击本程序使用图形界面。"
            )
            return
        from src.cli import 命令行
        命令行(参数)
        return

    # ---------- 无参数 ----------
    if 有控制台():
        # 命令行里被调用（无参数）→ REPL
        中文REPL().启动()
        return

    # 双击 + 无控制台 → GUI
    if 能启动图形():
        from src.gui import 启动图形
        _隐藏控制台_尝试()
        启动图形()
    else:
        _弹窗("当前环境无法启动图形界面，请使用命令行模式。")
        中文REPL().启动()


if __name__ == "__main__":
    main()