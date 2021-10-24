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
import mistletoe
from bs4 import BeautifulSoup, Tag
from functools import wraps


def list_block_wrap(func):
    @wraps(func)
    def wrapper(cls, node_arg):
        ret = []
        for children in node_arg.contents:
            if children == '\n':
                continue
            convert_result = getattr(cls, f'convert_{children.name}_elem')(children)
            if convert_result:
                ret.append(func(cls, convert_result))
        return ret

    return wrapper


class Block:
    @classmethod
    def convert_p_elem(cls, p_node: Tag):
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
    def convert_hr_elem(cls, hr_node):
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
    def convert_li_elem(cls, convert_result):
        return {
            "type": "text",
            "text": convert_result
        }

    @classmethod
    @list_block_wrap
    def convert_ul_elem(cls, convert_result):
        return {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "text": convert_result
            }
        }


if __name__ == '__main__':
    with open('/Users/zhangxinjian/Projects/PythonProject/mylearnlab/jupyter/myExercises/readme.md') as f:
        node = mistletoe.markdown(f.readlines())
    p = Block()
    soup = BeautifulSoup(node)
    ress = p.convert_ul_elem(soup)
    from pprint import pprint

    pprint(ress)
