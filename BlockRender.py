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

import mistletoe
from bs4 import BeautifulSoup
from functools import wraps
from loguru import logger


def list_block_wrap(func):
    @wraps(func)
    def wrapper(cls, node_arg):
        ret = []
        for children in node_arg.contents:
            if children == '\n' or children.name is None:
                continue
            elif children.name == 'i':
                ret += wrapper(cls, children)
                continue

            convert_result = getattr(cls, f'convert_{children.name}_elem')(children)

            if convert_result:
                ret.append(func(cls, convert_result))
        return ret

    return wrapper


class BlockRender:
    @classmethod
    def convert_p_elem(cls, p_node):
        if p_node.parent.name == 'li':
            return {
                "content": p_node.text,
                "link": None
            }
        return {
            "type": "paragraph",
            "paragraph": {
                "text": [{
                    "type": "text",
                    "text": {
                        "content": p_node.text,
                        "link": None
                    }
                }]
            },
        }

    @classmethod
    def convert_hr_elem(cls, _):
        return {
            "type": "divider",
            "divider": {}
        }

    @classmethod
    def convert_a_elem(cls, a_node):
        return {
            "content": a_node.text,
            "link": {
                "url": a_node.attrs.get('href')
            }
        }

    @classmethod
    @list_block_wrap
    def convert_li_elem(cls, convert_result: str):
        return {
            "type": "text",
            "text": convert_result
        }

    @classmethod
    @list_block_wrap
    def convert_ul_elem(cls, convert_result: str):
        return {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "text": convert_result
            }
        }

    @classmethod
    def convert_pre_elem(cls, pre_node):
        code_node = pre_node.code
        return {
            "type": "code",
            "code": {
                "text": [{
                    "type": "text",
                    "text": {
                        "content": code_node.text
                    }
                }],
                "language": code_node.attrs.get('class', ['language-text'])[0].replace('language-', '')
            }
        }

    @classmethod
    def convert_head_elem(cls, head_node):
        level = int(re.search(r'h(\d)', head_node.name).group(1))
        if level > 3:
            logger.warning(f'head level can`t over than 3, now is {level}')
            return
        return {
            "type": f"heading_{level}",
            f"heading_{level}": {
                "text": [{
                    "type": "text",
                    "text": {
                        "content": head_node.text,
                        "link": None
                    }
                }]
            }
        }

    @classmethod
    def convert_blockquote_elem(cls, quote_node):
        return {
            "type": "quote",
            "quote": {
                "text": [{
                    "type": "text",
                    "text": {
                        "content": quote_node.text,
                    },
                }],
            }
        }

    def content_iter(self, basic_node) -> list:
        """

        :param basic_node:
        :return:
        """
        ret = []
        for children in basic_node.contents:
            if children == '\n' or children is None:
                continue
            if children.name is None:
                logger.warning(f'skip empty node, {children}')
                continue
            if re.match(r'h\d', children.name):
                convert_result = self.convert_head_elem(children)
            else:
                convert_result = getattr(self, f'convert_{children.name}_elem')(children)

            if convert_result:
                if isinstance(convert_result, list):
                    ret += convert_result
                else:
                    ret.append(convert_result)
        return ret

    def main(self, md_path: str):
        with open(md_path) as f:
            node = mistletoe.markdown(f.readlines())
        soup = BeautifulSoup(node)

        ret = self.content_iter(soup)

        return ret


if __name__ == '__main__':
    md_path_ = '/Users/zhangxinjian/Projects/PythonProject/mylearnlab/jupyter/myExercises/readme.md'
    p = BlockRender()
    ress = p.main(md_path_)

    from pprint import pprint

    pprint(ress)
