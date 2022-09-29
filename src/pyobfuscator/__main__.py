import argparse
import logging
from .obfuscator import Obfuscator


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", type=str, required=True, help="source code path")
    parser.add_argument("-t", "--target", type=str, default=None, help="save obfuscated code to target path")
    parser.add_argument("-e", "--exclude_keys", nargs="+", default=None, help="excluded keywords won't be obfuscated")
    parser.add_argument("-v", "--verbose", type=int, default=0, help="log level for debug")
    parser.add_argument("-b", "--probability", type=int, default=0.5, help="probability of confuse line insertion")
    parser.add_argument("-r", "--repeat", type=int, default=5, help="Maximum insert number at same place")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    obfuscator = Obfuscator(args)
    obfuscator.obfuscate()
