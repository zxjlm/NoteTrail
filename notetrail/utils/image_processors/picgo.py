"""
@author: harumonia
@license: © Copyright 2023, Node Supply Chain Manager Corporation Limited.
@contact: zxjlm233@gmail.com
@software: Pycharm
@homepage: https://harumonia.moe/
@file: picgo.py
@time: 2023/1/11 10:04
@desc:
"""
from utils.image_processors import BaseImageUploader


class PicGoHandler(BaseImageUploader):
    def __init__(self):
        super().__init__()
        self.client = ""

    def upload_pic(self, path: str, filename: str):
        ...


picgo = PicGoHandler()
