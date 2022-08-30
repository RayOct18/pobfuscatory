import argparse
import logging
from .obfuscator import Obfuscator


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project", type=str, required=True)
    parser.add_argument("-d", "--dir", type=str, required=True)
    parser.add_argument("-t", "--target", type=str, default=None)
    parser.add_argument("-e", "--exclude_keys", nargs='+', default=None)
    parser.add_argument("-v", "--verbose", type=int, default=0)
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    obfuscator = Obfuscator(args.project, args.dir, args.target, args.exclude_keys)
    obfuscator.obfuscate()
