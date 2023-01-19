"""
@author: harumonia
@license: © Copyright 2022, Node Supply Chain Manager Corporation Limited.
@contact: zxjlm233@gmail.com
@software: Pycharm
@homepage: https://harumonia.moe/
@file: decorators.py
@time: 2022/4/10 21:54
@desc:
"""
import inspect
from datetime import datetime
from functools import wraps
from typing import Callable

from loguru import logger

LOGGING_FN = logger


def log(
    func: Callable = None,
    log_time: bool = True,
    log_args: bool = True,
    log_error: bool = True,
    log_file: str = None,
    logging_fn: Callable = None,
) -> Callable:
    """
    Tracks function time taken, arguments and errors
    Arguments:
        func: function to decorate
        log_time: whether to log time taken or not, default=True
        log_args: whether to log arguments or not, default=True
        log_error: whether to log error or not, default=True
        log_file: filepath where to write log, default=None
        logging_fn: log function (e.g. print, logger.info, rich console.print)
    Usage:
    ```python
    from deczoo import log
    @log
    def add(a, b): return a+b
    _ = add(1, 2)
    # add args=(a=1, b=2) time=0:00:00.000111
    ```
    """

    if logging_fn is None:
        logging_fn = LOGGING_FN

    @wraps(func)
    def wrapper(*args, **kwargs):

        tic = datetime.now()

        if log_args:

            func_args = inspect.signature(func).bind(*args, **kwargs).arguments
            func_args_str = ", ".join(f"{k}={v}" for k, v in func_args.items())

            optional_strings = [f"args=({func_args_str})"]

        else:
            optional_strings = []

        try:
            res = func(*args, **kwargs)
            toc = datetime.now()
            optional_strings += [
                f"time={toc - tic}" if log_time else None,
            ]

            return res

        except Exception as e:

            toc = datetime.now()
            optional_strings += [
                f"time={toc - tic}" if log_time else None,
                "Failed" + (f" with error: {e}" if log_error else ""),
            ]
            raise e

        finally:
            log_string = f"{func.__name__} {' '.join([s for s in optional_strings if s])}"
            logging_fn.info(log_string)

            if log_file is not None:
                with open(log_file, "a") as f:
                    f.write(f"{tic} {log_string}\n")

    return wrapper
