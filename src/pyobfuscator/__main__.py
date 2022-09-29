import argparse
import logging
from .obfuscator import Obfuscator


def validate_args(args):
    try:
        if not 0 <= args.probability <= 1:
            raise ValueError("probability must between 0 and 1")
        elif args.repeat < 0:
            raise ValueError("repeat must greater than 0")
    except ValueError as e:
        logging.error(f"argument: {e}")
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", type=str, required=True, help="source code path")
    parser.add_argument("-t", "--target", type=str, default=None, help="save obfuscated code to target path")
    parser.add_argument("-e", "--exclude_keys", nargs="+", default=None, help="excluded keywords won't be obfuscated")
    parser.add_argument("-v", "--verbose", type=int, default=0, help="log level for debug")
    parser.add_argument("-b", "--probability", type=float, default=0.5, help="probability of confuse line insertion")
    parser.add_argument("-r", "--repeat", type=int, default=5, help="Maximum insert number at same place")
    args = parser.parse_args()

    validate_args(args)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    obfuscator = Obfuscator(args)
    obfuscator.obfuscate()
