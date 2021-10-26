"""
@author: harumonia
@license: © Copyright 2021, Node Supply Chain Manager Corporation Limited.
@contact: zxjlm233@gmail.com
@software: Pycharm
@homepage: https://harumonia.moe/
@file: BookProcessor.py
@time: 2021/10/24 4:27 下午
@desc:
"""
import os

from CharacterScanner import CharacterScanner
from notion_client import Client


class BookProcessor:
    def __init__(self, database_id=None, page_id=None, client=None):
        if database_id or page_id is None:
            raise Exception('database or page must have one')
        self.database_id = database_id
        self.page_id = page_id
        self.notion = Client(auth=os.environ["NOTION_TOKEN"], client=client)

    def generate_character_block(self, child):
        name = os.path.basename(child)[:-3]
        return {
            'title': [
                {
                    'type': 'text',
                    'text': {'content': name},
                }
            ]
        }

    def dir_processor(self, dir_path: dict, root_page_id: str):
        """
        递归文件夹, 每次递归创建一个页面节点
        :param root_page_id:
        :param dir_path:
        :return:
        """
        for blocks, children in dir_path.items():
            if children:
                for child in children:
                    self.notion.pages.create(parent={"page_id": root_page_id},
                                             properties=self.generate_character_block(child))

    def file_processor(self, file_path):
        ...

    def main(self, path, book_name, book_url=None):
        path_dict = CharacterScanner().scanner(path)
        CharacterScanner.check_path(path_dict)

        if self.database_id:
            properties = {'Name': {'id': 'title',
                                   'type': 'title',
                                   'title': [
                                       {
                                           'type': 'text',
                                           'text': {'content': book_name, 'link': book_url},
                                       }
                                   ]
                                   },
                          }
            response = self.notion.pages.create({"parent": self.database_id, 'properties': properties})
            root_page_id = response.id
        else:
            ...
            # response = self.notion.blocks.children.append(parent=self.page_id)

        for blocks, children in path_dict.items():
            for block in blocks:
                self.file_processor(block, root_page_id)

            for child in children:
                self.dir_processor(child, root_page_id)
