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
    def wrapper(self, node_arg):
        ret = []

        for child in node_arg.contents:
            if child == '\n' or child.name is None:
                continue

            convert_result = getattr(self, f'convert_{child.name}_elem')(child)

            if convert_result:
                ret.append(convert_result)

        children = self.children_content(node_arg)
        return func(self, ret, children)

    return wrapper


class BlockRender:
    def convert_p_elem(self, p_node, children=None):
        return {
            "type": "paragraph",
            "paragraph": {
                "text": [{
                    "type": "text",
                    "text": {
                        "content": p_node.text,
                        "link": None
                    }
                }],
                "children": children
            },
        }

    def convert_hr_elem(self, _, __):
        return {
            "type": "divider",
            "divider": {}
        }

    def convert_a_elem(self, a_node, children=None):
        return {
            "content": a_node.text,
            "link": {
                "url": a_node.attrs.get('href')
            }
        }

    def convert_li_elem(self, li_node, children=None):
        return {
            "type": "text",
            "text": {
                'content': li_node.text
            },
        }

    @list_block_wrap
    def convert_ul_elem(self, convert_result: list, children=None):
        if children is None:
            children = []

        return {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "text": convert_result
            },
            "children": children
        }

    @list_block_wrap
    def convert_ol_elem(self, convert_result: list, children=None):
        return {
            "type": "numbered_list_item",
            "numbered_list_item": {
                "text": convert_result
            }
        }

    def convert_em_elem(self, em_node, children=None):
        print(em_node)

    def convert_pre_elem(self, pre_node, children=None):
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

    def convert_head_elem(self, head_node, children=None):
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

    def convert_blockquote_elem(self, quote_node, children=None):
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

    def convert_code_elem(self, code_node, children=None):
        # language = validate_language
        return {
            "type": "code",
            "code": {
                "text": [{
                    "type": "text",
                    "text": {
                        "content": code_node.text
                    }
                }],
                "language": "javascript"
            }
        }

    def content_iter(self, basic_node) -> list:
        """

        :param basic_node:
        :return:
        """
        ret = []
        for children in basic_node.contents:
            if not self.is_iterable_node(children):
                continue

            if children.name is None:
                convert_result = self.convert_p_elem(children)
            else:
                convert_result = self.parser_node_2_notion_style(children)

            if convert_result:
                if isinstance(convert_result, list):
                    ret += convert_result
                else:
                    ret.append(convert_result)
        return ret

    def parser_node_2_notion_style(self, node):
        if re.match(r'h\d', node.name):
            convert_result = self.convert_head_elem(node)
        else:
            convert_result = getattr(self, f'convert_{node.name}_elem')(node)
        return convert_result

    @staticmethod
    def is_iterable_node(node):
        if node == '\n' or node is None:
            return False
        # if node.name is None:
        #     logger.warning(f'skip empty node, {node.text}')
        #     return False

        return True

    def children_content(self, child_node):
        if not child_node.contents:
            return []
        if child_node == '\n' or child_node.name is None:
            return []

        return self.content_iter(child_node)

    def main(self, md_path: str):
        with open(md_path) as f:
            node = mistletoe.markdown(f.readlines())
        soup = BeautifulSoup(node)

        ret = self.content_iter(soup)

        return ret


if __name__ == '__main__':
    md_path_ = '/home/harumonia/projects/docs/note-book2-master/docs/ddd/00/README.md'
    p = BlockRender()
    ress = p.main(md_path_)

    from pprint import pprint

    pprint(ress)
