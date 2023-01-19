"""
@author: harumonia
@license: © Copyright 2021, Node Supply Chain Manager Corporation Limited.
@contact: zxjlm233@gmail.com
@software: Pycharm
@homepage: https://harumonia.moe/
@file: block.py
@time: 2021/10/24 10:49 上午
@desc:
"""
import re
from functools import wraps

import mistletoe
from bs4 import BeautifulSoup, Tag
from loguru import logger


def list_block_wrap(func):
    @wraps(func)
    def wrapper(cls, node_arg):
        ret, cv_list = [], []
        for children in node_arg.contents:
            if children == "\n" or children.name is None:
                continue
            convert_result = getattr(cls, f"convert_{children.name}_elem")(children)
            cv_list.append(convert_result)
        if cv_list:
            ret.append(func(cls, cv_list))
        return ret

    return wrapper


class BlockRender:
    """
    将md内容转为notion api内容
    """

    @classmethod
    def convert_p_elem(cls, p_node: Tag):
        """
        转换p标签

        p标签的转换比较复杂, 目前看来这是少数的可能存在子节点的标签.
        :param p_node:
        :return:
        """
        if p_node.parent.name == "li":
            return {"content": p_node.text, "link": None}
        # contents_type = [content for content in p_node.contents if not isinstance(content, NavigableString)]
        else:
            return {
                "type": "paragraph",
                "paragraph": {"text": cls.recursion_p_node(p_node)},
            }

    @classmethod
    def recursion_p_node(cls, p_node: Tag):
        ret = []
        for content in p_node.contents:
            ret.append(
                {
                    "type": "text",
                    "text": {
                        "content": content.text,
                        "link": {"type": "url", "url": content.attrs.get("href")} if content.name == "a" else None,
                    },
                }
            )
        return ret

    @classmethod
    def convert_hr_elem(cls, hr_node):
        return {"type": "divider", "divider": {}}

    @classmethod
    def convert_a_elem(cls, a_node: Tag):
        return {"content": a_node.text, "link": {"url": a_node.attrs.get("href")}}

    @classmethod
    def convert_li_elem(cls, li_node: Tag):
        return {"type": "text", "text": {"content": li_node.text, "link": None}}

    @classmethod
    @list_block_wrap
    def convert_ul_elem(cls, convert_result: str):
        return {"type": "bulleted_list_item", "bulleted_list_item": {"text": convert_result}}

    @classmethod
    @list_block_wrap
    def convert_ol_elem(cls, convert_result: str):
        return {"type": "numbered_list_item", "numbered_list_item": {"text": convert_result}}

    @classmethod
    def convert_pre_elem(cls, pre_node):
        language_list = [
            "abap",
            "arduino",
            "bash",
            "basic",
            "c",
            "clojure",
            "coffeescript",
            "c++",
            "c#",
            "css",
            "dart",
            "diff",
            "docker",
            "elixir",
            "elm",
            "erlang",
            "flow",
            "fortran",
            "f#",
            "gherkin",
            "glsl",
            "go",
            "graphql",
            "groovy",
            "haskell",
            "html",
            "java",
            "javascript",
            "json",
            "julia",
            "kotlin",
            "latex",
            "less",
            "lisp",
            "livescript",
            "lua",
            "makefile",
            "markdown",
            "markup",
            "matlab",
            "mermaid",
            "nix",
            "objective-c",
            "ocaml",
            "pascal",
            "perl",
            "php",
            "plain text",
            "powershell",
            "prolog",
            "protobuf",
            "python",
            "r",
            "reason",
            "ruby",
            "rust",
            "sass",
            "scala",
            "scheme",
            "scss",
            "shell",
            "sql",
            "swift",
            "typescript",
            "vb.net",
            "verilog",
            "vhdl",
            "visual basic",
            "webassembly",
            "xml",
            "yaml",
        ]
        code_node = pre_node.code
        language = code_node.attrs.get("class", ["language-text"])[0].replace("language-", "")
        if language == "text":
            language = "plain text"

        # 判断代码块语言是否支持
        if language not in language_list:
            for lan in language_list:
                if lan in language:
                    language = lan
                    break
            else:
                raise Exception("language can`t support.")

        return {
            "type": "code",
            "code": {"text": [{"type": "text", "text": {"content": code_node.text}}], "language": language},
        }

    @classmethod
    def convert_head_elem(cls, head_node):
        level = int(re.search(r"h(\d)", head_node.name).group(1))
        if level > 3:
            logger.warning(f"head level can`t over than 3, now is {level}")
            return
        return {
            "type": f"heading_{level}",
            f"heading_{level}": {"text": [{"type": "text", "text": {"content": head_node.text, "link": None}}]},
        }

    @classmethod
    def convert_blockquote_elem(cls, quote_node):
        return {
            "type": "quote",
            "quote": {
                "text": [
                    {
                        "type": "text",
                        "text": {
                            "content": quote_node.text,
                        },
                    }
                ],
            },
        }


class MarkdownRender:
    """
    渲染一篇markdown文档
    """

    def __init__(self):
        self.block_render = BlockRender()

    def process(self, md_path: str):
        with open(md_path) as f:
            node = mistletoe.markdown(f.readlines())
        soup = BeautifulSoup(node)

        ret = []
        for children in soup.contents:
            if children == "\n" or children is None:
                continue
            if re.match(r"h\d", children.name):
                convert_result = self.block_render.convert_head_elem(children)
            else:
                convert_result = getattr(self.block_render, f"convert_{children.name}_elem")(children)
            if convert_result:
                if isinstance(convert_result, list):
                    ret += convert_result
                else:
                    ret.append(convert_result)
        return ret


if __name__ == "__main__":
    path = "/Users/zhangxinjian/Projects/d2l/README.md"
    p = MarkdownRender()
    ress = p.process(path)

    from pprint import pprint

    pprint(ress)
