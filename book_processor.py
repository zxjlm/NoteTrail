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

from block_render import BlockRender
from character_scanner import CharacterScanner

from my_notion_client import notion_client
from notion_render import NotionRender, SuffixRender
from utils import markdown_render, BookInfo


class BookProcessor:
    def __init__(self, database_id=None, page_id=None):
        if (database_id or page_id) is None:
            raise Exception('database or page must have one')
        self.database_id = database_id
        self.page_id = page_id
        self.block_render = BlockRender()

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
                response = notion_client.create_page(parent={"page_id": root_page_id},
                                                     properties=self.generate_properties(title),
                                                     children=self.render_file(files_mapper[file_path]))
                dir_path['blocks'].remove(files_mapper[file_path])
                break
        else:
            # create a blank page
            response = notion_client.create_page(parent={"page_id": root_page_id},
                                                 properties=self.generate_properties(dir_path['path']))

        for block in dir_path['blocks']:
            self.file_processor(block, response['id'])
        for children in dir_path['children']:
            self.dir_processor(children, response['id'])

    def file_processor(self, file_path, page_id):
        logger.info('----------------> Processing file: {}'.format(file_path))
        response = notion_client.create_page(parent={"page_id": page_id},
                                             properties=self.generate_properties(file_path),
                                             children=self.render_file(file_path))
        sf = SuffixRender()
        sf.recursion_insert(response['id'])
        return response

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
    BookInfo.BOOK_PATH = '/home/harumonia/projects/docs/tmp'
    BookInfo.BOOK_NAME = 'Blog'
    p = BookProcessor(database_id='d0e931a36b43405996d118cf71957f6d')
    p.main()