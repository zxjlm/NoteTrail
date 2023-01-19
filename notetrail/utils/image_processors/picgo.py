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
from urllib.parse import urljoin

import requests
from utils.config_manager import config_manager
from utils.image_processors import BaseImageUploader, ImageUploadException


class PicGoHandler(BaseImageUploader):
    def __init__(self):
        super().__init__()
        self.client = ""

    def upload_pic(self, path: str, filename: str):
        body = {"list": [path]}
        response = requests.post(urljoin(f"http://{config_manager.config.pic_config.picgo_server}", "upload"), body)
        if response.json()["success"]:
            return response.json()["result"][0]
        else:
            raise ImageUploadException


picgo = PicGoHandler()
