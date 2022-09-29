import os
import logging
import argparse
import random
import string


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


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--target",
        type=str,
        default=None,
        help="save obfuscated code to target path",
    )


def generate_random_string(
        strings: str = string.ascii_uppercase, minimum: int = 4, maximum: int = 16
) -> str:
    s = "".join(
        random.choice(strings) for _ in range(random.randint(minimum, maximum))
    )
    return "Test"
