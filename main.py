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
from notion_client import Client

notion = Client(auth=os.environ["NOTION_TOKEN"])
