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

import httpx

from render import MarkdownRender
from CharacterScanner import CharacterScanner
from notion_client import Client
from loguru import logger


class BookProcessor:
    def __init__(self, database_id=None, page_id=None, client=None):
        if (database_id or page_id) is None:
            raise Exception('database or page must have one')
        self.database_id = database_id
        self.page_id = page_id
        self.notion = Client(auth=os.environ["NOTION_TOKEN"], client=client)
        self.md_render = MarkdownRender()

    def generate_character_block(self, raw_title=None):
        title = os.path.basename(raw_title)
        return {
            'title': [
                {
                    'type': 'text',
                    'text': {'content': title},
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
        logger.info(f'================= now start to parser dir: {dir_path} ===================')
        files_mapper = {os.path.basename(foo): foo for foo in dir_path['blocks']}
        md_file = files_mapper.get('README.md') or files_mapper.get('readme.md')
        if md_file:
            # if readme file exist, create a page base on readme
            # title = md_file[:-10]
            # response = self.notion.pages.create(parent={"page_id": root_page_id},
            #                                     properties=self.generate_character_block(title),
            #                                     children=self.md_render.process(md_file))
            self.notion.blocks.children.append(root_page_id, children=self.md_render.process(md_file))
            dir_path['blocks'].remove(md_file)
            generate_page_id = root_page_id
        else:
            # create a blank page
            response = self.notion.pages.create(parent={"page_id": root_page_id},
                                                properties=self.generate_character_block(dir_path['path']))
            generate_page_id = response['id']
        for block in dir_path['blocks']:
            self.file_processor(block, generate_page_id)
        for children in dir_path['children']:
            self.dir_processor(children, generate_page_id)

    def file_processor(self, file_path, page_id):
        logger.info(f'================= now start to parser file: {file_path} ===================')
        response = self.notion.pages.create(
            parent={"page_id": page_id},
            properties=self.generate_character_block(file_path),
            # children=self.md_render.process(file_path)
        )
        response_ = self.notion.blocks.children.append(response['id'], children=self.md_render.process(file_path))
        return response_

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
            response = self.notion.pages.create(parent={"database_id": self.database_id}, properties=properties)
            root_page_id = response['id']
        else:
            # response = self.notion.blocks.children.append(parent=self.page_id)
            print('page as root, todo')
            return

        for block in path_dict['blocks']:
            self.file_processor(block, root_page_id)

        for child in path_dict['children']:
            self.dir_processor(child, root_page_id)


if __name__ == '__main__':
    client = httpx.Client(proxies={'http://': 'http://127.0.0.1:7890', 'https://': 'http://127.0.0.1:7890'})
    p = BookProcessor(database_id='d0e931a36b43405996d118cf71957f6d', client=client)
    p.main('/Users/zhangxinjian/Projects/d2l', 'd2l')
