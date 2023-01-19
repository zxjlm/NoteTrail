"""
@author: harumonia
@license: © Copyright 2023, Node Supply Chain Manager Corporation Limited.
@contact: zxjlm233@gmail.com
@software: Pycharm
@homepage: https://harumonia.moe/
@file: config_manager.py
@time: 2023/1/9 16:13
@desc:
"""
from functools import cached_property
from pathlib import Path

import attrs
from loguru import logger
from rich import print
from yaml import Dumper, Loader, load

from notetrail.utils.utils import Bcolors, check_proxy_format

ALIOSS_REQUIRED_FIELDS = ["ali_oss_sk", "ali_oss_ak", "ali_bucket"]


@attrs.define
class PicConfig:
    picgo_server: str = attrs.field(default="", validator=check_proxy_format)
    ali_oss: dict = attrs.field(
        default={}, converter=lambda x: {} if all(not x.get(foo) for foo in ALIOSS_REQUIRED_FIELDS) else x
    )

    PRIORITY = ["picgo_server", "ali_oss"]

    @ali_oss.validator
    def check_oss_config(self, attribute, value: dict):
        """
        check ali_bucket, ali_oss_ak, ali_oss_sk
        :param attribute:
        :param value:
        :return:
        """
        pass
        # return all(not value.get(foo) for foo in AliOSSHandler.REQUIRED_FIELDS)

    @staticmethod
    def dict2config(value):
        if isinstance(value, PicConfig):
            return value
        else:
            return PicConfig(**value)

    def __repr__(self) -> str:
        s = [""]
        for foo in self.__attrs_attrs__:
            if isinstance(foo.repr, bool):
                s.append(f"{foo.name}: {getattr(self, foo.name)}")
            else:
                s.append(foo.repr(self.__getattribute__(foo.name)))
        return "\n  ".join(s)


@attrs.define
class ConfigFields:
    notion_token: str = attrs.field(default="1" * 20, repr=lambda x: f"{x[:5]}{'*' * (len(x) - 10)}{x[-5:]}")
    http_proxy: str = attrs.field(default="127.0.0.1:7890")
    pic_config: PicConfig = attrs.field(factory=PicConfig, converter=PicConfig.dict2config, repr=lambda x: x)


class ConfigManager:
    _REQUIRE_FIELDS = []
    path = Path(__file__).parent.parent.resolve().joinpath("config.yaml")
    config = ConfigFields()

    @classmethod
    def update(cls, file_path: str = ""):
        if file_path:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"{path} not exist!")
                exit(1)

            ConfigManager.path = path

        config_ = cls.load()
        cls.config = ConfigFields(**config_)

    @classmethod
    def load(cls):
        with open(cls.path) as f:
            config = load(f, Loader)
        return config

    @classmethod
    def display_config(cls):
        for foo in cls.config.__attrs_attrs__:
            if isinstance(foo.repr, bool):
                print(f"{foo.name}: {cls.config.__getattribute__(foo.name)}")
            else:
                print(f"{foo.name}: {foo.repr(cls.config.__getattribute__(foo.name))}")
        pic_processor = cls.select_pic_config()
        if pic_processor:
            print(f"Use {Bcolors.OKGREEN}{pic_processor}{Bcolors.ENDC} as picture processor.")
        else:
            print(f"{Bcolors.WARNING}unable to get a pic config, skip to handle picture.{Bcolors.ENDC}")

    @classmethod
    def select_pic_config(cls) -> str:
        """
        when multi pic config were scanned, select one base on priority.
        :return:
        """
        for field in PicConfig.PRIORITY:
            if getattr(cls.config.pic_config, field):
                return field
        else:
            return ""

    # def dump_config(self):
    #     ...


config_manager = ConfigManager()
