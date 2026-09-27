# -*- coding: utf-8 -*-
"""命令行模式"""
import os
import sys
import argparse

from .runtime import PandaRuntime
from .translator import PandaTranslator


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
        from .gui import 启动图形
        启动图形()
        return

    if args.command == "repl":
        from .repl import 中文REPL
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