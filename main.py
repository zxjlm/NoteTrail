"""
@author: harumonia
@license: © Copyright 2021, Node Supply Chain Manager Corporation Limited.
@contact: zxjlm233@gmail.com
@software: Pycharm
@homepage: https://harumonia.moe/
@file: main.py
@time: 2021/10/23 10:52 下午
@desc:
"""
import platform
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from utils import check_runtime, check_proxy_format

__version__ = "v0.1"
__module_name__ = "???"


def main():
    """
        Just main
        Returns:
        """

    version_string = (
        f"%(prog)s {__version__} \n "
        f"Python:  {platform.python_version()} \n"
    )

    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=f"{__module_name__} " f"(Version {__version__})",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=version_string,
        help="Display version information and dependencies.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        "-d",
        "--debug",
        action="store_true",
        dest="verbose",
        default=False,
        help="Display extra debugging information and metrics.",
    )
    parser.add_argument(
        "--proxy",
        default="127.0.0.1:7890",
        # action="store_const",
        # const="127.0.0.1:7890",
        dest="proxy",
        help="Use proxy. Default is 127.0.0.1:7890.",
    )

    args = parser.parse_args()

    if not check_runtime():
        print("Please set environment variable")
        exit(1)

    if args.proxy:
        if not check_proxy_format(args.proxy):
            print(f"Invalid proxy format: {args.proxy}")
            exit(1)
        import my_notion_client
        import httpx
        client_ = httpx.Client(proxies={'http://': f'http://{args.proxy}', 'https://': f'http://{args.proxy}'},
                               timeout=30)
        my_notion_client.notion_client = my_notion_client.MyNotionClient(client_)


if __name__ == '__main__':
    main()
