import sys
from .obfuscator import obfuscator


if __name__ == "__main__":
    project, path = sys.argv[1], sys.argv[2]
    obfuscator(project, path)
