import io
import json
import re
from datetime import datetime

import yaml
from loguru import logger

from notetrail.character_scanner import CharacterScanner
from notetrail.my_notion_client import notion_client
from notetrail.notion_render import NotionRender, SuffixRender
from notetrail.utils.utils import (
    BookInfo,
    RuntimeConfig,
    generate_digest_from_text,
    markdown_render,
)


class HexoParser:
    def __init__(self):
        self.property_map = {
            "date": self.date_parser,
            # 'updated': self.updated_parser,
            # 'update': self.updated_parser,
            "tags": self.tags_parser,
            "categories": self.categories_parser,
            "title": self.title_parser,
        }

    @staticmethod
    def update_properties(database_id):
        properties = {
            "Categories": {"multi_select": []},
            "Tags": {"multi_select": []},
            "HashValue": {"rich_text": []},
            "PostDate": {"date": {}},
        }
        notion_client.update_database_properties(database_id, properties=properties)

    @staticmethod
    def tags_parser(values: list):
        return {"Tags": {"type": "multi_select", "multi_select": [{"name": value} for value in values]}}

    @staticmethod
    def categories_parser(values: list):
        return {"Categories": {"multi_select": [{"name": value} for value in values]}}

    @staticmethod
    def updated_parser(value: datetime):
        return {"Last Edited Time": {"last_edited_time": value.isoformat()}}

    @staticmethod
    def date_parser(value):
        if isinstance(value, str):
            if re.match(r"\d{4}/\d{2}/\d{2}", value):
                value = datetime.strptime(value, "%Y/%m/%d %H:%M:%S")
        return {"PostDate": {"date": {"start": value.isoformat()}}}

    @staticmethod
    def title_parser(value: str):
        return {"title": {"title": [{"type": "text", "text": {"content": str(value)}}]}}

    @staticmethod
    def get_title(properties: dict):
        return properties["title"]["title"][0]["text"]["content"]

    @staticmethod
    def hash_parser(value: str):
        return {"HashValue": {"rich_text": [{"type": "text", "text": {"content": value}}]}}

    @staticmethod
    def get_hash(properties: dict):
        return properties["HashValue"]["rich_text"][0]["text"]["content"]

    def serialize_raw_property(self, property_dict):
        ...

    def main(self, property_dict):
        ret = {}

        for k, v in property_dict.items():
            if k in self.property_map and v:
                ret.update(self.property_map[k](v))

        hash_res = generate_digest_from_text(json.dumps(ret))
        ret.update(self.hash_parser(hash_res))

        return ret


class Collector:
    error_arts = []


class HexoProcessor:
    def __init__(self, database_id=None, page_id=None):
        if (database_id or page_id) is None:
            raise Exception("database or page must have one")
        self.database_id = database_id
        self.page_id = page_id

    def pre_parse_hexo_file(self, file_path):
        def extract_yaml_content():
            ret = []
            with open(file_path, "r") as f:
                lines = f.readlines()
                if lines[0].strip() != "---":
                    raise Exception(f"{file_path}: yaml header not found")
                for line in lines[1:]:
                    if line.strip() == "---":
                        break
                    ret.append(line)
            return "".join(ret)

        io_ = io.StringIO(extract_yaml_content())
        yaml_dict = yaml.safe_load(stream=io_)
        if yaml_dict.get("notion", True):
            property_dict = HexoParser().main(yaml_dict)
            return property_dict
        else:
            logger.info("schema notion is false, skip this file.")

    def generate_properties(self, file_path):
        return self.pre_parse_hexo_file(file_path)

    def file_processor(self, file_path, page_id):
        logger.info("----------------> Processing file: {}".format(file_path))
        properties = self.generate_properties(file_path)
        if properties is None:
            return

        full_title = HexoParser.get_title(properties)
        response = notion_client.search(query=full_title)

        for result in response.get("results", []):
            if result["properties"]["\ufeffName"]["title"][0]["plain_text"] == full_title:
                if result["properties"]["HashValue"]["rich_text"][0]["plain_text"] == HexoParser.get_hash(properties):
                    # 标题作为去重的键
                    logger.info(f"blog {full_title} has been in the notion")
                    return
                else:
                    logger.warning(f"blog {full_title} need to be updated")
                    notion_client.delete_block(result["id"])
        # ! 该段产生的异常不排除是代码出现 BUG, 所以不进行异常捕获, 一旦出现立刻结束程序, 避免浪费资源.

        try:
            children = self.render_file(file_path)
            response = notion_client.create_page(
                parent={"database_id": page_id}, properties=properties, children=children
            )
            sf = SuffixRender()
            sf.recursion_insert(response["id"])
        except Exception as _e:
            logger.exception(_e)
            Collector.error_arts.append({"title": full_title, "exception": str(_e), "file_path": file_path})
            return

    def main(self):
        path_dict = CharacterScanner().scanner()
        CharacterScanner.check_path(path_dict)

        for block in path_dict["blocks"]:
            self.file_processor(block, self.database_id)

    def render_file(self, md_path):
        def clean_annotation(text_):
            return re.sub("<!--.*?-->", "", text_)

        BookInfo.CURRENT_FILE_PATH = md_path
        with open(md_path) as f:
            lines = f.readlines()
            base = 2
            for idx, line in enumerate(lines):
                if line.strip() == "---" and idx > 2:
                    base = idx
                    break
            clean_text = clean_annotation("$%^&".join(lines[base:]))
            render_result = markdown_render(clean_text.split("$%^&"), NotionRender)
        return render_result


if __name__ == "__main__":
    BookInfo.BOOK_PATH = "/Users/zhangxinjian/Projects/NodeProject/zxjlm.github.io/source/_posts"  # 填入hexo的post文件组路径
    BookInfo.BOOK_NAME = "Blog"  # 标题名, 可自定
    database_id_ = RuntimeConfig.database_id
    HexoParser.update_properties(database_id_)
    p = HexoProcessor(database_id=database_id_)
    p.main()

    if Collector.error_arts:
        logger.error("存在如下的错误:")
        logger.error(Collector.error_arts)
