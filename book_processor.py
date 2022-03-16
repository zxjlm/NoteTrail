"""
@author: harumonia
@license: © Copyright 2021, Node Supply Chain Manager Corporation Limited.
@contact: zxjlm233@gmail.com
@software: Pycharm
@homepage: https://harumonia.moe/
@file: book_processor.py
@time: 2021/10/24 4:27 下午
@desc:
"""
import os

from loguru import logger

from character_scanner import CharacterScanner

from my_notion_client import notion_client
from notion_render import NotionRender, SuffixRender, WatcherClass
from utils import markdown_render, BookInfo, RuntimeConfig


class BookProcessor:
    IGNORE_FILES = [
        'CONTRIBUTING.md',
        'CODE_OF_CONDUCT.md',
        'SUMMARY.md'
    ]

    def __init__(self, database_id=None, page_id=None):
        if (database_id or page_id) is None:
            raise Exception('database or page must have one')
        self.database_id = database_id
        self.page_id = page_id

    def generate_title_property(self, file_path, raw_title=None):
        if not raw_title:
            raw_title = os.path.basename(file_path).replace('.md', '')
        return {
            'title': [
                {
                    'type': 'text',
                    'text': {'content': raw_title},
                }
            ]
        }

    def generate_properties(self, file_path, raw_title=None):
        return {
            'properties': self.generate_title_property(file_path, raw_title)
        }

    def dir_processor(self, dir_path: dict, root_page_id: str):
        """
        递归文件夹, 每次递归创建一个页面节点
        :param root_page_id:
        :param dir_path:
        :return:
        """
        files_mapper = {os.path.basename(foo): foo for foo in dir_path['blocks']}
        for file_path in files_mapper:
            # create a readme page
            if file_path.lower() == 'readme.md':
                title = files_mapper[file_path][:-10]
                properties = self.generate_properties(title)
                response = notion_client.create_page(parent={"page_id": root_page_id},
                                                     properties=properties['properties'],
                                                     children=self.render_file(files_mapper[file_path]))
                dir_path['blocks'].remove(files_mapper[file_path])
                break
        else:
            # create a blank page
            response = notion_client.create_page(parent={"page_id": root_page_id},
                                                 properties=self.generate_properties(dir_path['path'])['properties'])

        for block in dir_path['blocks']:
            self.file_processor(block, response['id'])
        for children in dir_path['children']:
            self.dir_processor(children, response['id'])

    def file_processor(self, file_path, page_id):
        logger.info('----------------> Processing file: {}'.format(file_path))
        if os.path.basename(file_path) in self.IGNORE_FILES:
            logger.info(f'ignore file {file_path}, skip it')
            return

        try:
            properties = self.generate_properties(file_path)
            children = self.render_file(file_path)
            response = notion_client.create_page(parent={"page_id": page_id},
                                                 properties=properties['properties'],
                                                 children=children)
            sf = SuffixRender()
            sf.recursion_insert(response['id'])
        except Exception as _e:
            # clean WatcherClass.DIGEST_TOKEN_FAMILY
            WatcherClass.DIGEST_TOKEN_FAMILY = []
            logger.exception(_e)
            logger.error(
                f'failed to convert md file, perhaps not in standard markdown format, or you can make a issue.')

    def main(self, book_url=None):
        path_dict = CharacterScanner().scanner()
        CharacterScanner.check_path(path_dict)

        if self.database_id:
            properties = {'Name': {'id': 'title',
                                   'type': 'title',
                                   'title': [
                                       {
                                           'type': 'text',
                                           'text': {'content': BookInfo.BOOK_NAME, 'link': book_url},
                                       }
                                   ]
                                   },
                          }
            response = notion_client.create_page(parent={"database_id": self.database_id}, properties=properties)
            root_page_id = response['id']
        else:
            # response = notion_client.blocks.children.append(parent=self.page_id)
            print('page as root, todo')
            return

        for block in path_dict['blocks']:
            self.file_processor(block, root_page_id)

        for child in path_dict['children']:
            self.dir_processor(child, root_page_id)

    def render_file(self, md_path):
        BookInfo.CURRENT_FILE_PATH = md_path
        with open(md_path) as f:
            render_result = markdown_render(f.readlines(), NotionRender)
        return render_result


if __name__ == '__main__':
    BookInfo.BOOK_PATH = '/Users/zhangxinjian/Projects/docs/sdn-handbook'  # 填入书的目录路径
    BookInfo.BOOK_NAME = 'sdn-handbook'  # 填入书的名称(可自定义)
    p = BookProcessor(database_id=RuntimeConfig.database_id)
    p.main()
