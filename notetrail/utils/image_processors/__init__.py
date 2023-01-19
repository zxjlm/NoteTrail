"""
@author: harumonia
@license: © Copyright 2023, Node Supply Chain Manager Corporation Limited.
@contact: zxjlm233@gmail.com
@software: Pycharm
@homepage: https://harumonia.moe/
@file: __init__.py.py
@time: 2023/1/11 09:51
@desc:
"""
from notetrail.utils.config_manager import PicConfig, config_manager


class ImageUploadException(Exception):
    ...


class BaseImageUploader:
    def __init__(self):
        self.bucket = None

    def validate_pic(self, name: str) -> bool:
        # raise NotImplementedError
        pass

    def upload_pic(self, path: str, filename: str):
        # raise NotImplementedError
        pass


pic_config = config_manager.select_pic_config()
if pic_config == "ali_oss":
    from .ali_oss import oss_handler

    image_processor = oss_handler
elif pic_config == "picgo_server":
    from .picgo import picgo

    image_processor = picgo
else:
    image_processor = BaseImageUploader()
