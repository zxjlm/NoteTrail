import io
from datetime import datetime

import yaml
from loguru import logger

from block_render import BlockRender
from character_scanner import CharacterScanner
from my_notion_client import notion_client
from notion_render import SuffixRender, NotionRender
from utils import BookInfo, markdown_render


class HexoParser:
    def __init__(self):
        self.property_map = {
            # 'date': self.date_parser,
            # 'updated': self.updated_parser,
            # 'update': self.updated_parser,
            'tags': self.tags_parser,
            'categories': self.categories_parser,
            'title': self.title_parser
        }

    @staticmethod
    def tags_parser(values: list):
        return {
            "Tags": {
                "type": "multi_select",
                "multi_select": [{"name": value} for value in values]
            }
        }

    @staticmethod
    def categories_parser(values: list):
        return {
            "Categories": {
                "multi_select": [{"name": value} for value in values]
            }
        }

    @staticmethod
    def updated_parser(value: datetime):
        return {
            "Last Edited Time": {
                "last_edited_time": value.isoformat()
            }
        }

    @staticmethod
    def date_parser(value: datetime):
        return {
            "Created Time": {
                "created_time": value.isoformat()
            }
        }

    @staticmethod
    def title_parser(value: str):
        return {
            "title": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": value
                        }
                    }
                ]
            }
        }

    def main(self, property_dict):
        ret = {}
        for k, v in property_dict.items():
            if k in self.property_map:
                ret.update(self.property_map[k](v))

        return ret


class HexoProcessor:
    def __init__(self, database_id=None, page_id=None):
        if (database_id or page_id) is None:
            raise Exception('database or page must have one')
        self.database_id = database_id
        self.page_id = page_id
        self.block_render = BlockRender()

    def pre_parse_hexo_file(self, file_path):
        def extract_yaml_content():
            ret = []
            with open(file_path, 'r') as f:
                lines = f.readlines()
                if lines[0].strip() != "---":
                    raise Exception(f'{file_path}: yaml header not found')
                for line in lines[1:]:
                    if line.strip() == '---':
                        break
                    ret.append(line)
            return ''.join(ret)

        io_ = io.StringIO(extract_yaml_content())
        yaml_dict = yaml.safe_load(stream=io_)
        property_dict = HexoParser().main(yaml_dict)
        return property_dict

    def generate_properties(self, file_path):
        return self.pre_parse_hexo_file(file_path)

    def file_processor(self, file_path, page_id):
        logger.info('----------------> Processing file: {}'.format(file_path))
        properties = self.generate_properties(file_path)
        children = self.render_file(file_path)
        response = notion_client.create_page(parent={"database_id": page_id}, properties=properties, children=children)
        sf = SuffixRender()
        sf.recursion_insert(response['id'])
        return response

    def main(self):
        path_dict = CharacterScanner().scanner()
        CharacterScanner.check_path(path_dict)

        for block in path_dict['blocks']:
            self.file_processor(block, self.database_id)

    def render_file(self, md_path):
        BookInfo.CURRENT_FILE_PATH = md_path
        with open(md_path) as f:
            lines = f.readlines()
            base = 2
            for idx, line in enumerate(lines):
                if line.strip() == '---' and idx > 2:
                    base = idx
                    break
            if lines.index('<!-- more -->\n'):
                lines.remove('<!-- more -->\n')
            render_result = markdown_render(lines[base:], NotionRender)
        return render_result


if __name__ == '__main__':
    BookInfo.BOOK_PATH = '/home/harumonia/projects/docs/tmp'
    BookInfo.BOOK_NAME = 'Blog'
    p = HexoProcessor(database_id='5dfca790-3787-4290-b22d-ec916bdc9f07')
    p.main()
