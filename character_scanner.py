"""
@author: harumonia
@license: © Copyright 2021, Node Supply Chain Manager Corporation Limited.
@contact: zxjlm233@gmail.com
@software: Pycharm
@homepage: https://harumonia.moe/
@file: character_scanner.py
@time: 2021/10/24 4:05 下午
@desc: 扫描目录下的md文件
"""
import glob
import os

from utils import Bcolors, BookInfo


class CharacterScanner:
    """
    扫描指定路径下所有能够转换的文件

    该类主要服务于之后复杂类型的文件转换

    目前只支持 markdown
    """

    # def __init__(self):
    #     self.basic_path = basic_path

    def recursion_scanner(self, current_path) -> dict:
        """

        param current_path:
        :return:
            {
                "blocks": [],
                "children": [],
                "path": ''
            }
        """
        path_list = glob.glob(f'{current_path}/*')

        md_files = {
            'blocks': [],
            'children': [],
            'path': current_path
        }

        for path_ in path_list:
            if os.path.isdir(path_):
                scan_res = self.recursion_scanner(path_)
                if scan_res['children'] or scan_res['blocks']:
                    md_files['children'].append(scan_res)
            elif path_.lower().endswith('.md'):
                md_files['blocks'].append(path_)
            else:
                continue

        return md_files

    @staticmethod
    def plain_recursion_scanner(current_path, depth=1):
        """

        :param depth:
        :param current_path:
        :return:
        """
        path_list = glob.glob(f'{current_path}/*')

        for path_ in path_list:
            if os.path.isdir(path_):
                CharacterScanner.plain_recursion_scanner(path_, depth + 1)
                print(Bcolors.OKBLUE + '-' * depth, os.path.basename(path_) + Bcolors.ENDC)
            elif path_.endswith('.md'):
                print(Bcolors.OKGREEN + '-' * depth, os.path.basename(path_) + Bcolors.ENDC)
            else:
                print(Bcolors.WARNING + '-' * depth, os.path.basename(path_) + Bcolors.ENDC)

    def scanner(self) -> dict:
        """
        指定扫描任务的根目录
        :return:
        """
        return self.recursion_scanner(BookInfo.BOOK_PATH)

    @staticmethod
    def check_path(path_dict):
        if path_dict.get('blocks') or path_dict.get('children'):
            return True
        raise Exception('there is no valid file or dir in root path.')


if __name__ == '__main__':
    BookInfo.BOOK_PATH = '/home/harumonia/projects/docs/w3-goto-world'
    import pprint
    p = CharacterScanner()
    # pprint.pprint(p.scanner())
    p.plain_recursion_scanner('/home/harumonia/projects/docs/w3-goto-world')
