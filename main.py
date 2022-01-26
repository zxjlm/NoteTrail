"""
@author: harumonia
@license: © Copyright 2021, Node Supply Chain Manager Corporation Limited.
@contact: zxjlm233@gmail.com
@software: Pycharm
@homepage: https://harumonia.moe/
@file: main.py
@time: 2021/10/23 10:52 下午
@desc:
"""

import os

import mistletoe
from bs4 import BeautifulSoup
from notion_client import Client

from BlockRender import BlockRender


if __name__ == '__main__':

    auth_token = os.environ.get("NOTION_TOKEN")
    if not auth_token:
        print("Please set NOTION_TOKEN environment variable")
        exit(1)

    notion = Client(auth=auth_token)

    with open('/Users/zhangxinjian/Projects/PythonProject/mylearnlab/jupyter/myExercises/readme.md') as f:
        node = mistletoe.markdown(f.readlines())
    p = BlockRender()
    soup = BeautifulSoup(node)
    ret = []
    for children in soup.contents:
        if children.name:
            cov = getattr(p, f'convert_{children.name}_elem')(children)
            if cov:
                if isinstance(cov, list):
                    ret += cov
                else:
                    ret.append(cov)
            else:
                print(f'{children} not found')
    notion.blocks.children.append("3543a8a4b8d1464d9e91f04cf864b84c", children=ret)
    # pprint(ret)
