# -*- coding: utf-8 -*-
"""PandaCode 运行时：翻译 + 执行"""
from .translator import PandaTranslator


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