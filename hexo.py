import io
import json
import re
from datetime import datetime

import yaml
from loguru import logger

from block_render import BlockRender
from character_scanner import CharacterScanner
from my_notion_client import notion_client
from notion_render import SuffixRender, NotionRender
from utils import BookInfo, markdown_render, generate_md5_from_text


class HexoParser:
    def __init__(self, database_id):
        self.property_map = {
            'date': self.date_parser,
            # 'updated': self.updated_parser,
            # 'update': self.updated_parser,
            'tags': self.tags_parser,
            'categories': self.categories_parser,
            'title': self.title_parser
        }
        self.database_id = database_id
        self.update_properties()

    def update_properties(self):
        properties = {
            "Categories": {
                "multi_select": []
            },
            'Tags': {
                "multi_select": []
            },
            "HashValue": {
                "rich_text": []
            },
            "PostDate": {
                "date": {}
            }
        }
        notion_client.update_database_properties(self.database_id, properties=properties)

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
    def date_parser(value):
        if isinstance(value, str):
            if re.match(r'\d{4}/\d{2}/\d{2}', value):
                value = datetime.strptime(value, '%Y/%m/%d %H:%M:%S')
        return {
            "PostDate": {
                "date": {
                    "start": value.isoformat()
                }
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

    @staticmethod
    def hash_parser(value: str):
        return {
            "HashValue": {
                "rich_text": [
                    {
                        "type": "text",
                        'text': {
                            "content": value
                        }
                    }
                ]
            }
        }

    def serialize_raw_property(self, property_dict):
        ...

    def main(self, property_dict):
        ret = {}

        for k, v in property_dict.items():
            if k in self.property_map:
                ret.update(self.property_map[k](v))

        hash_res = generate_md5_from_text(json.dumps(ret))
        ret.update(self.hash_parser(hash_res))

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
        if yaml_dict.get('notion', True):
            property_dict = HexoParser(self.database_id).main(yaml_dict)
            return property_dict
        else:
            raise Exception('notion: false')

    def generate_properties(self, file_path):
        return self.pre_parse_hexo_file(file_path)

    def file_processor(self, file_path, page_id):
        logger.info('----------------> Processing file: {}'.format(file_path))
        try:
            properties = self.generate_properties(file_path)
        except Exception as _e:
            if str(_e) == 'notion: false':
                return
            else:
                raise from _e
        children = self.render_file(file_path)
        response = notion_client.create_page(parent={"database_id": page_id}, properties=properties, children=children)
        sf = SuffixRender()
        sf.recursion_insert(response['id'])
        # return response

    def main(self):
        path_dict = CharacterScanner().scanner()
        CharacterScanner.check_path(path_dict)

        for block in path_dict['blocks']:
            self.file_processor(block, self.database_id)

    def render_file(self, md_path):
        def clean_annotation(text_):
            return re.sub('<!--.*?-->', '', text_)

        BookInfo.CURRENT_FILE_PATH = md_path
        with open(md_path) as f:
            lines = f.readlines()
            base = 2
            for idx, line in enumerate(lines):
                if line.strip() == '---' and idx > 2:
                    base = idx
                    break
            clean_text = clean_annotation('$%^&'.join(lines[base:]))
            render_result = markdown_render(clean_text.split('$%^&'), NotionRender)
        return render_result


if __name__ == '__main__':
    BookInfo.BOOK_PATH = '/home/harumonia/projects/my_project/zxjlm.github.io/source/_posts'
    BookInfo.BOOK_NAME = 'Blog'
    p = HexoProcessor(database_id='1e8487296745443fba236d02341c7c2d')
    p.main()
