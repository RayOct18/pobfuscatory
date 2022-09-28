import os
import logging


def log():
    formatter = logging.Formatter(
        "%(levelname)s %(asctime)s %(process)d %(thread)d [%(pathname)s:%(lineno)d] %(message)s"
    )
    handler = logging.StreamHandler(
        stream=None
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)


def startswith(folder):
    return os.path.join(
        "path", folder
    ).startswith("path")


def multiline_list(x, y, z):
    ls = [
        x, y,
        z
    ]
    return ls
