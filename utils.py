import os
import re
import hashlib

from mistletoe import Document


class RuntimeConfig:
    database_id = ''  # 数据库id


class BookInfo:
    BOOK_NAME = ""  # 书名(自定义)
    BOOK_PATH = ""  # 书存放的目录
    CURRENT_FILE_PATH = ""  # 不需要填
    # IS_HEXO = True


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def validate_language(language: str) -> bool:
    languages = ["abap", "arduino", "bash", "basic", "c", "clojure", "coffeescript", "c++", "c#", "css", "dart", "diff",
                 "docker", "elixir", "elm", "erlang", "flow", "fortran", "f#", "gherkin", "glsl", "go", "graphql",
                 "groovy", "haskell", "html", "java", "javascript", "json", "julia", "kotlin", "latex", "less", "lisp",
                 "livescript", "lua", "makefile", "markdown", "markup", "matlab", "mermaid", "nix", "objective-c",
                 "ocaml", "pascal", "perl", "php", "plain text", "powershell", "prolog", "protobuf", "python", "r",
                 "reason", "ruby", "rust", "sass", "scala", "scheme", "scss", "shell", "sql", "swift", "typescript",
                 "vb.net", "verilog", "vhdl", "visual basic", "webassembly", "xml", "yaml", "java/c/c++/c#"]
    if language in languages:
        return True
    return False


def markdown_render(iterable, renderer):
    """
    Converts markdown input to the output supported by the given renderer.
    If no renderer is supplied, ``HTMLRenderer`` is used.

    Note that extra token types supported by the given renderer
    are automatically (and temporarily) added to the parsing process.
    """
    with renderer() as renderer:
        return renderer.render(Document(iterable))


def erase_prefix_string(string, prefix):
    cnt = 0
    while cnt < len(prefix) and string[cnt] == prefix[cnt]:
        cnt += 1
    return string[cnt:]


def long_content_split_patch(content, max_length=2000):
    """
    Splits the content into multiple parts, each part is less than max_length.
    :param content:
    :param max_length:
    :return:
    """
    return [content[foo:foo + max_length] for foo in range(0, len(content), max_length)]


def check_runtime():
    """
    检查是否满足运行条件
    :return:
    """
    auth_token = os.environ.get("NOTION_TOKEN")

    # check oss config
    ak = os.environ.get("ALI_OSS_AK")
    sk = os.environ.get("ALI_OSS_SK")

    return auth_token and ak and sk


def check_proxy_format(proxy):
    if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+', proxy):
        return True
    return False


def generate_md5_from_text(text):
    m = hashlib.md5()
    m.update(text.encode("utf-8"))
    return m.hexdigest()
