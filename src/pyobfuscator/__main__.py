import sys
from .obfuscator import Obfuscator


if __name__ == "__main__":
    project, path = sys.argv[1], sys.argv[2]
    obfuscator = Obfuscator(project, path)
    obfuscator.obfuscate()
