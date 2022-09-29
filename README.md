# PyObfuscator

# Install
```bash
pip install git+https://github.com/RayOct18/pyobfuscator
```

# Usage
**Note:**
If your project use not built-in library, you need to install it first.
The obfuscator needs to scan all modules and functions from third-party libraries to exclude the keywords.

```bash
# single file
$ python -m pyobfuscator -s ./single_file/raw/hello_world.py -t ./obfuscated

# whole project
$ python -m pyobfuscator -s ./src/pyobfuscator -t ./examples/project/obfuscated

# preserve some key (obfuscator, Keys)
$ python -m pyobfuscator -s ./src/pyobfuscator -t ./examples/project/obfuscated -e obfuscator Keys

# adjust confuse line insertion, probability (0.0~1.0), repeat number(1~)
$ python -m pyobfuscator -s ./src/pyobfuscator -t ./examples/project/obfuscated -p 0.5 -r 5
# close confuse line
$ python -m pyobfuscator -s ./src/pyobfuscator -t ./examples/project/obfuscated -p 0

# open debug log
$ python -m pyobfuscator -s ./src/pyobfuscator -t ./examples/project/obfuscated -v 1
```

# Examples
**Single file:**
[ [raw](https://github.com/RayOct18/pyobfuscator/blob/main/examples/single_file/raw/hello_world.py) ]
[ [obfuscated](https://github.com/RayOct18/pyobfuscator/blob/main/examples/single_file/obfuscated/VGWPPEYHANJ.py) ]

**Whole project:**
[ [raw](https://github.com/RayOct18/pyobfuscator/tree/main/src/pyobfuscator) ]
[ [obfuscated](https://github.com/RayOct18/pyobfuscator/tree/main/examples/project/obfuscated) ]
