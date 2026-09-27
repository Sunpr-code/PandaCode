# -*- coding: utf-8 -*-
"""PandaCode 翻译器：中文 → Python"""
import re
from .keywords import KEYWORDS, OPERATORS, PUNCTUATION


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