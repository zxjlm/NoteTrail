from mistletoe import Document


class BookInfo:
    BOOK_NAME = ""
    BOOK_PATH = ""
    CURRENT_FILE_PATH = ""


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
