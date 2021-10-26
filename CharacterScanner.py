"""
@author: harumonia
@license: © Copyright 2021, Node Supply Chain Manager Corporation Limited.
@contact: zxjlm233@gmail.com
@software: Pycharm
@homepage: https://harumonia.moe/
@file: CharacterScanner.py
@time: 2021/10/24 4:05 下午
@desc: 扫描目录下的md文件
"""
import glob
import os


class CharacterScanner:
    """
    扫描指定路径下所有能够转换的文件

    该类主要服务于之后复杂类型的文件转换

    目前只支持 markdown
    """

    def __init__(self):
        ...

    def recursion_scanner(self, current_path) -> dict:
        """

        :param current_path:
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
            elif path_.endswith('.md'):
                md_files['blocks'].append(path_)
            else:
                continue

        return md_files

    def scanner(self, path: str) -> dict:
        """
        指定扫描任务的根目录
        :param path:
        :return:
        """
        return self.recursion_scanner(path)

    @staticmethod
    def check_path(path_dict):
        if path_dict.get('blocks') or path_dict.get('children'):
            return True
        raise Exception('there is no valid file or dir in root path.')


if __name__ == '__main__':
    p = CharacterScanner()
    print(p.scanner('/Users/zhangxinjian/Projects/w3-goto-wold'))
